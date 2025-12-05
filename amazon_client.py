# amazon_client.py – NO PROXY, HEADERS REALI 2025 – SPACCA AMAZON
import requests
from bs4 import BeautifulSoup
import random
import time
import logging
from config import AMAZON_ASSOC_TAG

def add_affiliate_tag(url):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={AMAZON_ASSOC_TAG}"

def get_offers(keywords="offerte lampo", max_items=10):
    # URL freschi 2025 per offerte IT
    urls = [
        "https://www.amazon.it/gp/goldbox",
        "https://www.amazon.it/deals",
        "https://www.amazon.it/s?k=offerte+del+giorno&i=deals",
    ]

    # User-Agent reali Chrome/Firefox 2025 (rotanti)
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
    ]

    # Headers anti-bot 2025 (copia da browser dev tools)
    headers_template = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    offers = []
    session = requests.Session()
    session.headers.update(headers_template)

    for attempt in range(5):  # 5 retry con delay random
        for url in urls:
            try:
                logging.info(f"Tentativo {attempt+1}/5 - URL: {url}")
                time.sleep(random.uniform(1, 3))  # Delay umano
                
                r = session.get(url, timeout=15)
                if r.status_code != 200 or "robot" in r.text.lower() or "access denied" in r.text.lower():
                    logging.warning(f"Bloccato su {url} (status: {r.status_code})")
                    continue

                soup = BeautifulSoup(r.content, "html.parser")

                # Selettori aggiornati 2025 per deals/cards
                cards = (soup.select("div[data-asin]") or 
                         soup.select("[cel_widget_id*='DEAL']") or 
                         soup.select("div.s-result-item") or 
                         soup.find_all("div", class_=lambda x: x and "deal" in x.lower() if x else False))[:20]

                if not cards:
                    logging.warning(f"Nessuna card trovata su {url}")
                    continue

                for card in cards:
                    # Link
                    a_tag = card.find("a", class_="a-link-normal") or card.find("a", href=True)
                    if not a_tag or not a_tag.get("href"):
                        continue
                    raw_url = a_tag["href"]
                    if not raw_url.startswith("http"):
                        raw_url = "https://www.amazon.it" + raw_url
                    full_url = add_affiliate_tag(raw_url)

                    # Title
                    title_elem = (card.find("h2") or 
                                  card.find("span", {"data-component-type": "s-search-results"}) or 
                                  card.find("div", class_="a-row a-size-base"))
                    title = title_elem.get_text(strip=True)[:150] if title_elem else "Offerta Amazon"

                    if len(title) < 5:
                        continue

                    # Price
                    price_elem = (card.find("span", class_="a-price-whole") or 
                                  card.find("span", class_="a-offscreen") or 
                                  card.find("span", class_="a-color-price"))
                    price = price_elem.get_text(strip=True) if price_elem else "Vedi prezzo"

                    # Image
                    img_elem = card.find("img")
                    image = (img_elem["src"] if img_elem and img_elem.get("src") else 
                             img_elem["data-a-dynamic-image"] if img_elem and img_elem.get("data-a-dynamic-image") else 
                             "https://m.media-amazon.com/images/G/01/x-locale/common/transparent-pixel.gif")
                    if isinstance(image, dict):
                        image = list(image.keys())[0]

                    offers.append({
                        "title": title,
                        "url": full_url,
                        "image": image,
                        "price": price,
                        "currency": "€"
                    })

                    logging.info(f"Trovata: {title[:50]}...")

                if len(offers) >= max_items:
                    logging.info(f"SPARATE {len(offers)} offerte! Tentativo {attempt+1}")
                    return offers[:max_items]

            except Exception as e:
                logging.error(f"Errore su {url}: {e}")
                time.sleep(random.uniform(2, 5))  # Backoff
                continue

    logging.warning("Tutti i tentativi falliti, ma continuo...")
    return offers  # Ritorna quello che ha, anche vuoto
