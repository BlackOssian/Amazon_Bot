# amazon_client.py – PROXY ROTANTI FREE 2025 – PER AMAZON IT
import requests
from bs4 import BeautifulSoup
import random
import time
import logging
from config import AMAZON_ASSOC_TAG

def add_affiliate_tag(url):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={AMAZON_ASSOC_TAG}"

# Proxy freschi da ProxyScrape – aggiornati 5 dic 2025, HTTP anonimi per IT scraping
PROXY_POOL = [
    "http://103-174-102-103:80",  # IT-friendly
    "http://154-197-165-8:8800",
    "http://43-135-164-2:13001",
    "http://117-160-192-178:8080",
    "http://47-74-152-29:8888",
    "http://38-154-194-22:8800",
    "http://185-199-229-156:7492",  # EU low-latency
    "http://185-199-228-220:7302",
    "http://81-16-222-3:80",  # IT direct
    "http://93-189-183-154:80",
]

def get_random_proxy():
    proxy = random.choice(PROXY_POOL)
    return {"http": proxy, "https": proxy}

def get_offers(keywords="offerte lampo", max_items=10):
    urls = [
        "https://www.amazon.it/gp/goldbox",
        "https://www.amazon.it/deals",
        "https://www.amazon.it/s?k=offerte+del+giorno&i=deals&rh=n%3A412609031",
    ]

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36",
    ]

    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }

    offers = []
    session = requests.Session()
    session.headers.update(headers)

    for attempt in range(5):  # 5 giri con proxy diversi
        proxy = get_random_proxy()
        logging.info(f"Tentativo {attempt+1}/5 con proxy: {proxy['http'][-10:]}...")

        for url in urls:
            try:
                time.sleep(random.uniform(2, 4))  # Delay anti-bot
                r = session.get(url, proxies=proxy, timeout=15)
                
                if r.status_code != 200 or "access denied" in r.text.lower() or "robot" in r.text.lower():
                    logging.warning(f"Bloccato su {url} (status: {r.status_code})")
                    continue

                soup = BeautifulSoup(r.content, "lxml")  # lxml più veloce

                # Selettori aggiornati per deals 2025
                cards = (soup.select("div[data-asin]") +
                         soup.select(".s-result-item") +
                         soup.select("[cel_widget_id*='DEAL']"))[:25]

                if not cards:
                    logging.warning(f"Nessuna card su {url}")
                    continue

                for card in cards:
                    # Link e title
                    a = card.find("a", class_="a-link-normal") or card.find("a", href=True)
                    if not a:
                        continue
                    raw_url = a["href"]
                    if not raw_url.startswith("http"):
                        raw_url = "https://www.amazon.it" + raw_url
                    full_url = add_affiliate_tag(raw_url)

                    title = (card.find("h2") or card.find("span", class_="a-size-base-plus") or a).get_text(strip=True)[:150]
                    if len(title) < 10 or "amazon" in title.lower() and len(title) < 50:  # Skip placeholder
                        continue

                    # Price
                    price_elem = card.find("span", class_="a-price-whole") or card.find("span", class_="a-offscreen") or card.find("span", class_="a-color-price")
                    price = price_elem.get_text(strip=True) if price_elem else "Scopri offerta"

                    # Image
                    img = card.find("img")
                    image = img["src"] if img and img.get("src") else img.get("data-a-dynamic-image", "")
                    if isinstance(image, dict):
                        image = list(image.keys())[0]
                    if not image or image.startswith("data:"):
                        image = "https://m.media-amazon.com/images/G/01/storewide/heroes/2025/12days/12days_670x300._CB303000000_.jpg"  # Placeholder deal

                    offers.append({
                        "title": title,
                        "url": full_url,
                        "image": image,
                        "price": price,
                        "currency": "€"
                    })
                    logging.info(f"Trovata: {title[:50]}... Prezzo: {price}")

                if len(offers) >= max_items:
                    logging.info(f"BOOM! {len(offers)} offerte sparate con proxy {proxy['http'][-10:]}")
                    return offers[:max_items]

            except Exception as e:
                logging.error(f"Errore proxy/URL: {e}")
                time.sleep(random.uniform(3, 6))  # Backoff più lungo

    logging.warning("Proxy pool esausto, ma riprovo tra 4 ore...")
    return offers  # Qualsiasi cosa abbia preso
