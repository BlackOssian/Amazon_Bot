# amazon_client.py – PROXY FRESCI 5 DIC 2025 + FALLBACK NO PROXY – SPACCA AMAZON
import requests
from bs4 import BeautifulSoup
import random
import time
import logging

AMAZON_ASSOC_TAG = "darkitalia-21"

def add_affiliate_tag(url):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={AMAZON_ASSOC_TAG}"

# Proxy freschi da ProxyScrape – elite HTTP, last checked 5 dic 2025, low latency
PROXY_POOL = [
    "http://108.162.192.116:80",  # Canada, elite, 91ms
    "http://108.162.192.147:80",  # Canada, elite, 101ms
    "http://101.128.107.36:80",   # Indonesia, transparent, 2162ms (usa se desperate)
    "http://185.199.229.156:7492", # EU, anonimo
    "http://81.16.222.3:80",      # IT direct
    "http://93.189.183.154:80",   # EU
]

def get_random_proxy():
    return {"http": random.choice(PROXY_POOL), "https": random.choice(PROXY_POOL)}

def get_offers(keywords="offerte del giorno", max_items=10):
    urls = [
        "https://www.amazon.it/gp/goldbox",
        "https://www.amazon.it/deals",
        "https://www.amazon.it/s?k=offerte+del+giorno"
    ]

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
    ]

    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "it-IT,it;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    offers = []
    session = requests.Session()
    session.headers.update(headers)

    # Prima prova con proxy (3 tentativi)
    for attempt in range(3):
        proxy = get_random_proxy()
        logging.info(f"Tentativo proxy {attempt+1}/3: {proxy['http'][-10:]}...")

        for url in urls:
            try:
                time.sleep(random.uniform(1, 3))
                r = session.get(url, proxies=proxy, timeout=15)

                if r.status_code != 200 or len(r.text) < 5000:
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

                    price = (card.find("span", class_="a-offscreen") or card.find("span", class_="a-price-whole")).get_text(strip=True) if card.find("span", class_="a-offscreen") else "Scopri prezzo"

                    img = card.find("img")
                    image = img["src"] if img and img.get("src") else "https://via.placeholder.com/300?text=Amazon+Deal"

                    offers.append({
                        "title": title,
                        "url": full_url,
                        "image": image,
                        "price": price,
                        "currency": "€"
                    })
                    logging.info(f"Trovata con proxy: {title[:50]}...")

                if len(offers) >= max_items:
                    logging.info(f"BOOM PROXY! {len(offers)} offerte sparate")
                    return offers

            except Exception as e:
                logging.error(f"Proxy fallito: {e}")

    # Fallback NO PROXY (ultima chance, diretto da Render IP)
    logging.info("Proxy esausti – fallback NO PROXY")
    for url in urls:
        try:
            time.sleep(random.uniform(2, 4))
            r = session.get(url, timeout=20)  # No proxy qui

            if r.status_code != 200:
                continue

            soup = BeautifulSoup(r.content, "lxml")
            cards = soup.select("div[data-asin]")[:15] or soup.select(".s-result-item")[:15]

            for card in cards:
                # Stesso parsing di prima...
                a = card.find("a", href=True)
                if not a: continue
                raw_url = a["href"]
                if not raw_url.startswith("http"):
                    raw_url = "https://www.amazon.it" + raw_url
                full_url = add_affiliate_tag(raw_url)

                title = (card.find("h2") or card.find("span", class_="a-size-base-plus") or a).get_text(strip=True)[:150]
                if len(title) < 10: continue

                price = (card.find("span", class_="a-offscreen") or card.find("span", class_="a-price-whole")).get_text(strip=True) if card.find("span", class_="a-offscreen") else "Scopri prezzo"

                img = card.find("img")
                image = img["src"] if img and img.get("src") else "https://via.placeholder.com/300?text=Amazon+Deal"

                offers.append({
                    "title": title,
                    "url": full_url,
                    "image": image,
                    "price": price,
                    "currency": "€"
                })
                logging.info(f"Trovata NO PROXY: {title[:50]}...")

            if len(offers) >= max_items // 2:  # Anche solo 5 bastano
                logging.info(f"BOOM FALLBACK! {len(offers)} offerte dal diretto")
                return offers

        except Exception as e:
            logging.error(f"No proxy fallito: {e}")

    return offers  # Qualsiasi merda abbia preso, meglio di zero
