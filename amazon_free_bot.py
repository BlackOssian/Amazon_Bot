import re
import random
import time
import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot
import os

# ================= CONFIG (metti tutto in config.py o direttamente qui) =================
TELEGRAM_BOT_TOKEN = "8281603203:AAEkKvUNgJs_khi7KDXfc1xGEjtCKalP2ts" # il tuo
TELEGRAM_CHANNEL_USERNAME = "@OfferteAmazon" # il tuo
AMAZON_TRACKING_ID = "darkitalia-21" # il tuo

# RIPORTATO AL VALORE DESIDERATO (25%)
MIN_DISCOUNT = 25 # pubblica solo ≥25% 
WAIT_MINUTES = 7 # controllo ogni 7 minuti (più offerte)

# URL più stabile: cerchiamo direttamente nella pagina dei risultati di ricerca
URLS_TO_CHECK = [
    "https://www.amazon.it/s?k=offerte+del+giorno",
]

PUBLISHED_FILE = "published_asins.txt"
# ====================================================================================

headers = {
    "User-Agent": random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_1) AppleWebKit/537.36 Chrome/137.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1"
    ]),
    "Accept-Language": "it-IT,it;q=0.9",
}

def load_published():
    if not os.path.exists(PUBLISHED_FILE):
        return set()
    with open(PUBLISHED_FILE, encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_published(asin):
    with open(PUBLISHED_FILE, "a", encoding="utf-8") as f:
        f.write(asin + "\n")

def get_deals():
    published = load_published()
    deals = []
    unique_asins_session = set() 

    for url in URLS_TO_CHECK:
        print(f"Scraping: {url}")
        try:
            time.sleep(random.uniform(2, 5))
            r = requests.get(url, headers=headers, timeout=20, verify=False) 
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            # STRATEGIA PER PAGINA DI RICERCA: Cerca tutti i risultati del componente s-search-result
            result_items = soup.find_all("div", {"data-component-type": "s-search-result"})
            
            if not result_items:
                print("DEBUG: Nessun risultato di ricerca trovato con 'data-component-type: s-search-result'.")
            
            for item in result_items:
                asin = item.get("data-asin")
                if not asin or len(asin) != 10 or asin in published or asin in unique_asins_session:
                    continue
                
                unique_asins_session.add(asin)

                # --- 1. Estrazione Titolo ---
                title_tag = item.find('h2 a span') 
                title = title_tag.get_text(strip=True) if title_tag else "No titolo"

                # --- 2. Estrazione Prezzo e Sconto (logica basata sul prezzo barrato) ---
                price = "N/D"
                discount = 0
                
                # Prezzo finale (a-offscreen all'interno del blocco di prezzo)
                current_price_tag = item.find("span", class_="a-price")
                if current_price_tag:
                    price_offscreen = current_price_tag.find("span", class_="a-offscreen")
                    if price_offscreen:
                        price = price_offscreen.get_text(strip=True)
                        current_price_text = price.replace('€', '').replace(',', '.').strip()
                        
                        # Prezzo di Listino (tag barrato)
                        list_price_tag = item.find("span", class_="a-text-strike")
                        
                        if list_price_tag:
                            list_price_text = list_price_tag.get_text().replace('€', '').replace(',', '.').strip()
                            
                            try:
                                current_price_float = float(current_price_text)
                                list_price_float = float(list_price_text)

                                if list_price_float > current_price_float:
                                    discount = int(100 * (1 - (current_price_float / list_price_float)))
                                
                                # Log dettagliato anche se lo sconto è < 25% (per il debug)
                                if current_price_float > 0 and discount > 0:
                                     print(f"[DEBUG] ASIN: {asin} | Sconto calcolato: {discount}% | Prezzo: {price} | Titolo: {title[:40]}...")

                            except ValueError:
                                pass # Il parsing non è riuscito, mantieni lo sconto a 0

                # --- 3. Filtro e Aggiunta ---
                if discount >= MIN_DISCOUNT and price != "N/D" and len(title) > 10:
                    link = f"https://www.amazon.it/dp/{asin}?tag={AMAZON_TRACKING_ID}"
                    deals.append({"asin": asin, "title": title, "price": price, "discount": discount, "link": link})
                    print(f"Found: {asin} – {discount}% – {price} – {title[:60]}")

        except requests.exceptions.RequestException as req_e:
            print(f"Errore nella richiesta HTTP su {url}: {req_e}")
            time.sleep(random.randint(30, 60))
        except Exception as e:
            print(f"Errore generico su {url}: {e}")

    return deals

async def post_deal(deal, bot):
    msg = (
        f"🔥 *OFFERTA LAMPO {deal['discount']}%* 🔥\n\n"
        f"🏷️ *{deal['title']}*\n\n"
        f"💶 *Prezzo: {deal['price']}* (-{deal['discount']}%)\n\n"
        f"🔗 [ACQUISTA SUBITO]({deal['link']})"
    )
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHANNEL_USERNAME, 
            text=msg, 
            parse_mode="Markdown", 
            disable_web_page_preview=False
        )
        print(f"Postata: {deal['title'][:50]}...")
        return True
    except Exception as e:
        print(f"Errore Telegram: {e}")
        return False

async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    print("Bot GRATUITO Offerte Lampo avviato – controlla ogni 7 minuti")
    print(f"Filtro Offerte Attivo: MIN_DISCOUNT è impostato a {MIN_DISCOUNT}%")

    while True:
        print(f"\n{time.strftime('%H:%M')} – Cerco nuove offerte...", end="\r") 
        
        new_deals = get_deals()

        for deal in new_deals:
            if await post_deal(deal, bot):
                save_published(deal["asin"])
                await asyncio.sleep(8) 

        if not new_deals:
            print(f"{time.strftime('%H:%M')} – Nessuna nuova offerta trovata.             ") 

        await asyncio.sleep(WAIT_MINUTES * 60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot fermato")