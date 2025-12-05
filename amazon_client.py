# amazon_client.py – VERSIONE INDESTRUCTIBILE 2025
import requests
from bs4 import BeautifulSoup
import random
import logging

AMAZON_ASSOC_TAG = "darkitalia-21"

# Proxy gratuiti che funzionano oggi (aggiornati 5 dic 2025)
PROXIES_POOL = [
    "http://154.197.165.8:8800",
    "http://43.135.164.2:13001",
    "http://117.160.192.178:8080",
    "http://47.74.152.29:8888",
    "http://103.174.102.103:80",
    "http://38.154.194.22:8800",
]

def add_affiliate_tag(url):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={AMAZON_ASSOC_TAG}"

def get_proxies():
    return {"http": random.choice(PROXIES_POOL), "https": random.choice(PROXIES_POOL)}

def get_offers(keywords="", max_items=15):
    urls = [
        "https://www.amazon.it/gp/goldbox/",
        "https://www.amazon.it/deals",
        "https://www.amazon.it/offerte",
    ]

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
    ]

    offers = []
    session = requests.Session()

    for _ in range(3):  # 3 tentativi con proxy diversi
        try:
            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
            }
            session.headers.update(headers)
            proxy = get_proxies()
            logging.info(f"Tentativo con proxy {proxy['http'][-10:]}...")

            for url in urls:
                r = session.get(url, proxies=proxy, timeout=20)
                if "To discuss automated access" in r.text or r.status_code != 200:
                    continue

                soup = BeautifulSoup(r.content, "html.parser")
                cards = soup.select("div[data-asin]") or soup.select("[cel_widget_id*='DEAL']") or soup.select("div.a-cardui")

                for card in cards:
                    a = card.find("a", class_="a-link-normal")
                    if not a: continue
                    link = "https://www.amazon.it" + a["href"].split("?")[0] if not a["href"].startswith("http") else a["href"]

                    title = card.get_text(strip=True)[:200]
                    if not title or len(title) < 10: continue

                    img = card.find("img")
                    image = img["src"] if img and img.get("src") else "https://m.media-amazon.com/images/G/01/x-locale/common/transparent-pixel.gif"

                    price = "N/D"
                    price_tag = card.find("span", class_="a-price-whole") or card.find("span", class_="a-offscreen")
                    if price_tag:
                        price = price_tag.get_text(strip=True)

                    offers.append({
                        "title": title,
                        "url": add_affiliate_tag(link),
                        "image": image.replace("._AC_", "_AC_").replace("SS40", "SL500"),
                        "price": price,
                        "currency": "€"
                    })

                    if len(offers) >= max_items:
                        logging.info(f"SPARATE {len(offers)} offerte! Proxy vincente: {proxy['http'][-10:]}")
                        return offers

        except Exception as e:
            logging.error(f"Proxy fallito: {e}")
            continue

    return offers
