import re
import random
import time
import asyncio
import os
from playwright.async_api import async_playwright
from telegram import Bot
import urllib3
from bs4 import BeautifulSoup

# Disabilita warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Importa dal config.py
from config import *

PUBLISHED_ASIN_FILE = "published_asins.txt"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
]

MIN_DISCOUNT_PERCENTAGE = 0  # Rilassato: pubblica anche 0% se prezzo valido (ma filtra >20% in Telegram?)


def load_published_asins():
    if not os.path.exists(PUBLISHED_ASIN_FILE):
        return set()
    with open(PUBLISHED_ASIN_FILE, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())


def save_published_asin(asin):
    with open(PUBLISHED_ASIN_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{asin}\n")


async def scrape_amazon_for_deals(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=300)  # Più veloce
        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={'width': 1920, 'height': 1080},
            locale='it-IT',
            extra_http_headers={'Accept-Language': 'it-IT,it;q=0.9,en;q=0.8'}
        )
        page = await context.new_page()

        try:
            print(f"Caricamento pagina: {url}")
            await page.goto(url, wait_until='domcontentloaded', timeout=45000)
            await page.wait_for_load_state('networkidle', timeout=15000)  # Più tempo per JS
            await page.wait_for_timeout(7000)  # Aspetta animazioni BF/carousel

            # Scroll avanzato per caricare TUTTI i deals (3x per sicurezza)
            for _ in range(3):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
                await page.wait_for_timeout(2000)
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 2 / 3)")
                await page.wait_for_timeout(2000)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(4000)

            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')

            found_deals = []
            seen_asins = set()

            # Selettori ULTRA-ESPANSI per /deals + /blackfriday 2025
            product_blocks = (
                soup.find_all('div', attrs={'data-asin': True}) or
                soup.find_all('div', class_=re.compile(r'(octopus-pc-item|pcard|deal-card|grid-col|carousel-card|pcard-carousel)', re.I)) or
                soup.find_all('li', class_=re.compile(r'(octopus|deal|item|pcard)', re.I)) or
                soup.find_all('div', class_=re.compile(r'a-section\s+octopus', re.I))
            )

            print(f"Trovati {len(product_blocks)} blocchi prodotto dopo scroll avanzato.")

            for block in product_blocks[:30]:  # Più blocchi
                try:
                    # ASIN: Priorità alta
                    asin = block.get('data-asin') or block.get('data-pid')
                    if not asin:
                        link = block.find('a', href=re.compile(r'/dp/|/gp/product/'))
                        if link:
                            asin_match = re.search(r'/dp/([A-Z0-9]{10})|/gp/product/([A-Z0-9]{10})', link.get('href', ''))
                            asin = asin_match.group(1) if asin_match else asin_match.group(2) if asin_match else None

                    if not asin or asin in seen_asins or len(asin) != 10:
                        continue
                    seen_asins.add(asin)

                    full_url = f"https://www.amazon.it/dp/{asin}"
                    aff_link = f"{full_url}?tag={AMAZON_TRACKING_ID}"

                    # === TITOLO: 6+ Fallback ===
                    title = "Offerta senza titolo"
                    title_selectors = [
                        'h2 span.a-size-base-plus.a-color-base.a-text-normal',
                        'h2 span.a-size-medium.a-color-base',
                        'h3 span.a-size-base',
                        'span[data-testid="product-title"]',
                        'span.a-size-base-plus.a-color-base.a-text-normal',
                        'div.a-row.a-size-base span.a-size-base-plus'
                    ]
                    for sel in title_selectors:
                        title_elem = block.select_one(sel)
                        if title_elem and title_elem.get_text(strip=True):
                            title = title_elem.get_text(strip=True)
                            break
                    if len(title) < 8 and 'senza' in title:  # Fallback img
                        img = block.find('img', alt=True)
                        if img and img.get('alt', '').strip():
                            title = img['alt'].strip()[:150]

                    # === PREZZO: 7+ Fallback + Pulizia ===
                    price = "N/D"
                    price_selectors = [
                        'span.a-offscreen',
                        'div.a-row.a-size-base.a-color-price span.a-offscreen',
                        'span[data-testid="price"]',
                        '.a-price.aok-align-center span.a-offscreen',
                        'span.a-price-whole + span.a-price-fraction',
                        '.a-price span.a-color-price'
                    ]
                    for sel in price_selectors:
                        price_elem = block.select_one(sel)
                        if price_elem:
                            raw_price = price_elem.get_text(strip=True)
                            if re.search(r'\d+[,]\d{2}', raw_price):
                                price = raw_price
                                break

                    # Fallback parti + assemblaggio
                    if price == "N/D":
                        parts = []
                        for cls in ['a-price-symbol', 'a-price-whole', 'a-price-fraction']:
                            part_elem = block.find('span', class_=re.compile(cls))
                            if part_elem:
                                parts.append(part_elem.get_text(strip=True))
                        if parts:
                            price = ''.join(parts).strip()
                            if price and '€' not in price:
                                price += ' €'

                    # Pulizia: solo prezzi validi
                    price = re.sub(r'[^\d,€\s]', '', price).strip()
                    if not re.search(r'\d+[,]\d{2}', price):
                        price = "N/D"

                    # === SCONTO: 5+ Fallback + Regex Potenziato ===
                    discount = 0
                    discount_selectors = [
                        'span.a-badge-text',
                        'div.a-badge-text__container span.a-badge-text',
                        'span.a-size-small.a-color-price',
                        'span[data-testid="discount"]',
                        '.a-color-price:contains("%")'
                    ]
                    for sel in discount_selectors:
                        discount_elem = block.select_one(sel)
                        if discount_elem:
                            text = discount_elem.get_text()
                            match = re.search(r'(-?(\d+))%', text)
                            if match:
                                discount = abs(int(match.group(1)))
                                break

                    # Fallback testo libero (caso comune in /deals)
                    if discount == 0:
                        all_text = block.get_text()
                        matches = re.findall(r'(risparmi?a|off|sconto|save)\s*(-?\d+)%', all_text, re.I)
                        if matches:
                            discount = abs(int(matches[0][1]))

                    # Debug RAW per ogni blocco (aiuta a debug)
                    print(f"RAW BLOCK {asin}: Titolo='{title[:40]}...' | Prezzo='{price}' | Sconto={discount}%")

                    # Filtro RILASSATO: Priorità a prezzi validi + titolo decente
                    if len(title) > 8 and price != "N/D" and discount >= MIN_DISCOUNT_PERCENTAGE:
                        found_deals.append({
                            'asin': asin,
                            'title': title[:180],  # Telegram limit
                            'price': price,
                            'discount': discount,
                            'link': aff_link
                        })
                        print(f"✅ VALID DEAL: {asin} | {discount}% | {price} | {title[:50]}...")

                except Exception as e:
                    print(f"Errore su blocco {asin if 'asin' in locals() else 'N/A'}: {e}")
                    continue

            await browser.close()
            print(f"Trovate {len(found_deals)} offerte valide dopo filtri.")
            return found_deals

        except Exception as e:
            print(f"Errore caricamento pagina: {e}")
            await browser.close()
            return []


async def post_to_telegram(deal, bot):
    # Filtra in Telegram: solo >20% per non spam
    if deal['discount'] < 20:
        print(f"⏭️ Sconto basso ({deal['discount']}%) - Salto post: {deal['title'][:30]}")
        return False

    message = (
        f"*🔥 OFFERTA {deal['discount']}% OFF! 🔥*\n\n"
        f"*{deal['title']}*\n\n"
        f"💰 *Prezzo:* {deal['price']}\n\n"
        f"[🛒 Acquista ADESSO]({deal['link']})"
    )

    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHANNEL_USERNAME,
            text=message,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        print(f"✅ POSTATA: {deal['title'][:40]}... ({deal['discount']}%)")
        return True
    except Exception as e:
        print(f"❌ Errore Telegram: {e}")
        return False


async def main():
    print("🚀 Avvio bot Amazon Deals V3.0 (BF 2025 - Live Optimized)...")
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    published_asins = load_published_asins()
    print(f"ASIN caricati: {len(published_asins)}")

    while True:
        print(f"\n{'='*70}")
        print(f"Nuovo ciclo - {time.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*70}")

        deals = await scrape_amazon_for_deals(TEST_AMAZON_URL)

        new_posts = 0
        for deal in deals:
            asin = deal['asin']
            if asin not in published_asins:
                if await post_to_telegram(deal, bot):
                    save_published_asin(asin)
                    published_asins.add(asin)
                    new_posts += 1
                    await asyncio.sleep(random.uniform(5, 10))  # Anti-flood
            else:
                print(f"⏭️ Già postata: {asin}")

        if not deals:
            print("❌ 0 deals: Prova URL='https://www.amazon.it/blackfriday' o headless=False per debug visivo.")
        else:
            print(f"✅ {new_posts} nuove postate su {len(deals)} totali trovate.")

        print("⏳ Prossimo ciclo tra 15 min...")
        await asyncio.sleep(900)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot fermato. Ciao!")