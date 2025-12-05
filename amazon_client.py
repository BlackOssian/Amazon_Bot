# amazon_client.py – VERSIONE FINALE SENZA SELENIUM – PROXY FREE 2025
import requests
from bs4 import BeautifulSoup
import random
import time
import logging

AMAZON_ASSOC_TAG = "darkitalia-21"  # se non usi config.py, lascialo così

def add_affiliate_tag(url):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={AMAZON_ASSOC_TAG}"

# Proxy HTTP anonimi freschi al 5 dicembre 2025 (testati su Amazon.it)
PROXY_POOL = [
    "http://103.174.102.103:80",
    "http://154.197.165.8:8800",
    "http://43.135.164.2:13001",
    "http://117.160.192.178:8080",
    "http://47.74.152.29:8888",
    "http://38.154.194.22:8800",
    "http://185.199.229.156:7492",
    "http://185.199.228.220:7302",
    "http://81.16.222.3:80",
    "http://93.189.183.154:80",
]

def get_random_proxy():
    proxy = random.choice(PROXY_POOL)
    return {"http": proxy, "https": proxy}

def get_offers(keywords="offerte lampo", max_items=10):
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

    for _ in range(6):  # 6 tentativi con proxy diversi
        proxy = get_random_proxy()
        logging.info(f"Tentativo con proxy {proxy['http'][-12:]}")

        for url in urls:
            try:
                time.sleep(random.uniform(2, 5))
                r = session.get(url, proxies=proxy, timeout=20, allow_redirects=True)

                if r.status_code != 200 or len(r.text) < 10000:
                    continue

                soup = BeautifulSoup(r.content, "lxml")

                cards = soup.select("div[data-asin]")[:20]
                if not cards:
                    cards = soup.select(".s-result-item")[:20]

                for card in cards:
                    a = card.find("a", class_="a-link-normal")
                    if not a: continue

                    link = "https://www.amazon.it" + a["href"].split("?")[0] if "/dp/" in a["href"] else a["href"]
                    full_url = add_affiliate_tag(link)

                    title = card.find("h2")
                    if not title: continue
                    title = title.get_text(strip=True)[:150]

                    price = card.find("span", class_="a-offscreen")
                    price = price.get_text(strip=True) if price else "Scopri prezzo"

                    img = card.find("img")
                    image = img["src"] if img and img.get("src") else "https://m.media-amazon.com/images/G/01/x-locale/common/transparent-pixel.gif"

                    offers.append({
                        "title": title,
                        "url": full_url,
                        "image": image,
                        "price": price,
                        "currency": "€"
                    })

                    if len(offers) >= max_items:
                        logging.info(f"Trovate e pronte {len(offers)} offerte!")
                        return offers

            except Exception as e:
                logging.error(f"Errore: {e}")

    return offers  # anche se poche o zero
