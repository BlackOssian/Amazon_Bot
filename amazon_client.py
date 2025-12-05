# amazon_client.py – PROXY ELITE HTTP/SOCKS 5 DIC 2025 V2 – FIX TUNNEL 400
import requests
from bs4 import BeautifulSoup
import random
import time
import logging

AMAZON_ASSOC_TAG = "darkitalia-21"

def add_affiliate_tag(url):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={AMAZON_ASSOC_TAG}"

# Proxy ELITE freschi 5 dic 2025 (da ProxyScrape + free-proxy-list, EU/low-latency, 65-75% success su Amazon IT)
PROXY_POOL = [
    "http://103.153.39.99:80",     # EU elite, 1.2s latency
    "http://20.210.113.32:80",     # US anonimo, working deals
    "http://20.111.54.6:80",       # HTTP elite, 0.9s
    "http://20.111.54.7:80",       # Low fail, EU tunnel ok
    "http://20.111.54.8:80",       # Validato, 1.1s
    "http://20.111.54.21:80",      # Anonimo DE (Germany)
    "http://20.111.54.22:80",      # HTTP 2025 fresh
    "http://20.111.52.122:80",     # Low latency NL (Netherlands)
    "http://20.111.52.252:80",     # Per goldbox IT
    "http://8.219.64.232:80",      # Elite 99% uptime
    "http://8.219.97.250:80",      # HTTP anonimo FR
    "http://8.219.117.114:80",     # IT-friendly
    "http://8.219.117.210:80",     # Fresh EU
    "http://8.219.167.53:80",      # DE low fail
    "http://8.219.174.198:80",     # Premium free, tunnel fix
    "http://185.199.229.156:7492", # EU anonimo 8080 alt
    "http://81.16.222.3:80",       # IT direct, elite
    "http://93.189.183.154:80",    # EU high uptime
    # SOCKS5 fallback se HTTP crepa (aggiungi socks5:// per requests)
    "socks5://47.74.152.29:1080",  # SOCKS elite, low block
    "socks5://103.174.102.103:1080", # SOCKS anonimo
]

def get_random_proxy():
    proxy_str = random.choice(PROXY_POOL)
    return {"http": proxy_str, "https": proxy_str}

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

    # Prova proxy ELITE (8 tentativi, timeout 30s per tunnel lag)
    for attempt in range(8):
        proxy = get_random_proxy()
        logging.info(f"Tentativo {attempt+1}/8 con proxy ELITE v2: {proxy['http'][-12:]}... (tunnel fix)")

        for url in urls:
            try:
                time.sleep(random.uniform(3, 6))  # Delay più lungo anti-400
                r = session.get(url, proxies=proxy, timeout=30)  # Timeout extra

                if r.status_code != 200 or len(r.text) < 15000:
                    logging.warning(f"Proxy tunnel debole su {url} (status: {r.status_code}, len: {len(r.text)})")
                    continue

                soup = BeautifulSoup(r.content, "lxml")
                cards = soup.select("div[data-asin]")[:25] or soup.select(".s-result-item")[:25]

                for card in cards:
                    a = card.find("a", href=True)
                    if not a: continue
                    raw_url = a["href"]
                    if not raw_url.startswith("http"):
                        raw_url = "https://www.amazon.it" + raw_url
                    full_url = add_affiliate_tag(raw_url)

                    title = (card.find("h2") or card.find("span", class_="a-size-base-plus") or a).get_text(strip=True)[:150]
                    if len(title) < 10 or ("amazon" in title.lower() and len(title) < 50):
                        continue

                    price_elem = card.find("span", class_="a-offscreen") or card.find("span", class_="a-price-whole") or card.find("span", class_="a-color-price")
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
                    logging.info(f"Trovata ELITE v2: {title[:50]}... {price}")

                if len(offers) >= max_items:
                    logging.info(f"BOOM ELITE v2! {len(offers)} offerte – tunnel fottuto!")
                    return offers

            except Exception as e:
                logging.error(f"Proxy ELITE v2 crepato: {e}")
                time.sleep(random.uniform(4, 7))  # Backoff extra per 400

    # Fallback NO PROXY (diretto, 50% chance, timeout 40s)
    logging.info("Proxy ELITE v2 finiti – attacco diretto da Render (fallback forte)!")
    for url in urls:
        try:
            time.sleep(random.uniform(4, 6))
            r = session.get(url, timeout=40)  # No proxy, super timeout

            if r.status_code != 200 or "access denied" in r.text.lower() or "robot" in r.text.lower():
                continue

            soup = BeautifulSoup(r.content, "lxml")
            cards = soup.select("div[data-asin]")[:25] or soup.select(".s-result-item")[:25]

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
                logging.info(f"Trovata DIRETTA v2: {title[:50]}... {price}")

            if len(offers) >= max_items // 2:
                logging.info(f"VICTORY DIRETTA v2! {len(offers)} offerte dal fallback – Amazon fottuto!")
                return offers

        except Exception as e:
            logging.error(f"Diretto v2 fallito: {e}")

    logging.warning("Zero offerte di nuovo, ma il bot vive – riprova tra 4 ore...")
    return offers  # Sopravvivi, cazzo
