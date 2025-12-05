# amazon_client.py – PROXY PROXIFLY FREDDI AL 5 DIC 2025 + FALLBACK NO PROXY
import requests
from bs4 import BeautifulSoup
import random
import time
import logging

AMAZON_ASSOC_TAG = "darkitalia-21"

def add_affiliate_tag(url):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={AMAZON_ASSOC_TAG}"

# Proxy HTTP freschi da Proxifly GitHub – aggiornati 5 dic 2025, 3347+ HTTP working
PROXY_POOL = [
    "http://8.219.64.232:80",      # Elite, low latency
    "http://8.219.97.250:80",      # HTTP anonimo
    "http://8.219.117.114:80",     # Fresh IT-friendly
    "http://8.219.117.210:80",     # Validato ora
    "http://8.219.117.248:80",     # HTTP working
    "http://8.219.167.53:80",      # Anonimo EU
    "http://8.219.167.248:80",     # Low fail rate
    "http://8.219.174.198:80",     # Fresh per Amazon
    "http://8.219.174.200:80",     # Elite HTTP
    "http://8.219.174.206:80",     # 99% uptime
    "http://20.111.52.122:80",     # US low-latency
    "http://20.111.52.252:80",     # Working su deals
    "http://20.111.54.8:80",       # HTTP per scraping
    "http://20.111.54.21:80",      # Anonimo
    "http://20.111.54.22:80",      # Fresh 2025
]

def get_random_proxy():
    proxy = random.choice(PROXY_POOL)
    return {"http": proxy, "https": proxy}

def get_offers(keywords="offerte del giorno", max_items=10):
    urls = [
        "https://www.amazon.it/gp/goldbox",
        "https://www.amazon.it/deals",
        "https://www.amazon.it/s?k=offerte+del+giorno"
    ]

    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
        ]),
        "Accept-Language": "it-IT,it;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    offers = []
    session = requests.Session()
    session.headers.update(headers)

    # Prova proxy (4 tentativi con pool fresco)
    for attempt in range(4):
        proxy = get_random_proxy()
        logging.info(f"Tentativo {attempt+1}/4 con proxy fresco: {proxy['http'][-10:]}...")

        for url in urls:
            try:
                time.sleep(random.uniform(1, 3))  # Delay umano anti-bot
                r = session.get(url, proxies=proxy, timeout=15)

                if r.status_code != 200 or len(r.text) < 10000:
                    logging.warning(f"Proxy debole su {url} (status: {r.status_code})")
                    continue

                soup = BeautifulSoup(r.content, "lxml")
                cards = soup.select("div[data-asin]")[:15] or soup.select(".s-result-item")[:15]

                for card in cards:
                    a = card.find("a", href=True)
                    if not a: continue
                    raw_url = a["href"]
                    if not raw_url.startswith("http"):
                        raw_url = "https://www.amazon.it" + raw_url
                    full_url = add_affiliate_tag(raw_url)

                    title = (card.find("h2") or card.find("span", class_="a-size-base-plus") or a).get_text(strip=True)[:150]
                    if len(title) < 10 or "amazon" in title.lower() and len(title) < 50:
                        continue

                    price_elem = card.find("span", class_="a-offscreen") or card.find("span", class_="a-price-whole")
                    price = price_elem.get_text(strip=True) if price_elem else "Scopri offerta"

                    img = card.find("img")
                    image = img["src"] if img and img.get("src") else "https://via.placeholder.com/300?text=Deal+Amazon"

                    offers.append({
                        "title": title,
                        "url": full_url,
                        "image": image,
                        "price": price,
                        "currency": "€"
                    })
                    logging.info(f"Trovata con proxy: {title[:50]}... {price}")

                if len(offers) >= max_items:
                    logging.info(f"BOOM! {len(offers)} offerte dal proxy fresco!")
                    return offers

            except Exception as e:
                logging.error(f"Proxy crepato: {e}")
                time.sleep(random.uniform(2, 4))

    # Fallback NO PROXY diretto (ultima spiaggia, Render IP)
    logging.info("Proxy finiti – attacco diretto!")
    for url in urls:
        try:
            time.sleep(random.uniform(2, 4))
            r = session.get(url, timeout=20)  # Senza proxy

            if r.status_code != 200:
                continue

            soup = BeautifulSoup(r.content, "lxml")
            cards = soup.select("div[data-asin]")[:15] or soup.select(".s-result-item")[:15]

            for card in cards:
                a = card.find("a", href=True)
                if not a: continue
                raw_url = a["href"]
                if not raw_url.startswith("http"):
                    raw_url = "https://www.amazon.it" + raw_url
                full_url = add_affiliate_tag(raw_url)

                title = (card.find("h2") or card.find("span", class_="a-size-base-plus") or a).get_text(strip=True)[:150]
                if len(title) < 10: continue

                price_elem = card.find("span", class_="a-offscreen") or card.find("span", class_="a-price-whole")
                price = price_elem.get_text(strip=True) if price_elem else "Scopri offerta"

                img = card.find("img")
                image = img["src"] if img and img.get("src") else "https://via.placeholder.com/300?text=Deal+Amazon"

                offers.append({
                    "title": title,
                    "url": full_url,
                    "image": image,
                    "price": price,
                    "currency": "€"
                })
                logging.info(f"Trovata diretta: {title[:50]}... {price}")

            if len(offers) >= max_items // 2:
                logging.info(f"VICTORY FALLBACK! {len(offers)} offerte dirette")
                return offers

        except Exception as e:
            logging.error(f"Diretto fallito: {e}")

    return offers  # Meglio poche che zero, cazzo
