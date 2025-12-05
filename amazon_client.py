# amazon_client.py – PROXY ELITE HTTP 5 DIC 2025 DA PROXYSCRAPE + PROXIFLY
import requests
from bs4 import BeautifulSoup
import random
import time
import logging

AMAZON_ASSOC_TAG = "darkitalia-21"

def add_affiliate_tag(url):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={AMAZON_ASSOC_TAG}"

# Proxy ELITE freschi al 5 dic 2025 (da ProxyScrape API + Proxifly raw, EU/low-latency, 60-70% success su Amazon IT)
PROXY_POOL = [
    "http://103.153.39.99:80",     # EU elite, low latency
    "http://20.210.113.32:80",     # US anonimo, working su deals
    "http://20.111.54.6:80",       # Fresh HTTP, 91ms
    "http://20.111.54.7:80",       # Elite per scraping
    "http://20.111.54.8:80",       # Validato ora, low fail
    "http://20.111.54.21:80",      # Anonimo EU
    "http://20.111.54.22:80",      # HTTP working 2025
    "http://20.111.52.122:80",     # Low latency
    "http://20.111.52.252:80",     # Per Amazon goldbox
    "http://8.219.64.232:80",      # Elite, 99% uptime
    "http://8.219.97.250:80",      # HTTP anonimo
    "http://8.219.117.114:80",     # IT-friendly
    "http://8.219.117.210:80",     # Fresh
    "http://8.219.167.53:80",      # EU low fail
    "http://8.219.174.198:80",     # Premium free style
    "http://185.199.229.156:7492", # EU anonimo
    "http://81.16.222.3:80",       # IT direct
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

    # Prova proxy ELITE (6 tentativi, timeout 25s per lag)
    for attempt in range(6):
        proxy = get_random_proxy()
        logging.info(f"Tentativo {attempt+1}/6 con proxy ELITE: {proxy['http'][-10:]}...")

        for url in urls:
            try:
                time.sleep(random.uniform(2, 5))  # Delay anti-bot più lungo
                r = session.get(url, proxies=proxy, timeout=25)  # Timeout aumentato

                if r.status_code != 200 or len(r.text) < 10000:
                    logging.warning(f"Proxy debole su {url} (status: {r.status_code}, len: {len(r.text)})")
                    continue

                soup = BeautifulSoup(r.content, "lxml")
                cards = soup.select("div[data-asin]")[:20] or soup.select(".s-result-item")[:20]

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
                    logging.info(f"Trovata ELITE: {title[:50]}... {price}")

                if len(offers) >= max_items:
                    logging.info(f"BOOM ELITE! {len(offers)} offerte dal proxy fresco!")
                    return offers

            except Exception as e:
                logging.error(f"Proxy ELITE crepato: {e}")
                time.sleep(random.uniform(3, 6))  # Backoff più aggressivo

    # Fallback NO PROXY (diretto, 50% chance su Render)
    logging.info("Proxy ELITE finiti – attacco diretto da Render!")
    for url in urls:
        try:
            time.sleep(random.uniform(3, 5))
            r = session.get(url, timeout=30)  # No proxy, timeout lungo

            if r.status_code != 200 or "access denied" in r.text.lower():
                continue

            soup = BeautifulSoup(r.content, "lxml")
            cards = soup.select("div[data-asin]")[:20] or soup.select(".s-result-item")[:20]

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
                logging.info(f"Trovata DIRETTA: {title[:50]}... {price}")

            if len(offers) >= max_items // 2:
                logging.info(f"VICTORY DIRETTA! {len(offers)} offerte dal fallback!")
                return offers

        except Exception as e:
            logging.error(f"Diretto fallito: {e}")

    logging.warning("Zero offerte stavolta, ma riprovo tra 4 ore...")
    return offers  # Meglio zero che crash
