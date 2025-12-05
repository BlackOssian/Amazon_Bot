import requests
from bs4 import BeautifulSoup
from config import AMAZON_ASSOC_TAG

def add_affiliate_tag(url, tag):
    if "?" in url:
        return f"{url}&tag={tag}"
    else:
        return f"{url}?tag={tag}"

def get_offers(keywords="offerte", max_items=5):
    # AGGIUNTO https:// QUI
    search_url = "https://www.amazon.it"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Errore durante il recupero della pagina Amazon: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    offers = []

    items = soup.find_all('div', {'data-component-type': 's-search-result'})

    if not items:
        items = soup.find_all('li', class_='a-carousel-card')

    for item in items:
        title_tag = item.find('h2', class_='a-size-mini')
        price_tag = item.find('span', class_='a-offscreen') or item.find('span', class_='a-color-price')
        url_tag = item.find('a', class_='a-link-normal')
        image_tag = item.find('img', class_='s-image') or item.find('img', class_='a-lazy-loaded')

        if title_tag and price_tag and url_tag and image_tag:
            title = title_tag.get_text(strip=True)
            relative_url = url_tag['href']

            full_url = add_affiliate_tag(f"https://www.amazon.it{relative_url}", AMAZON_ASSOC_TAG)

            image_url = image_tag['src']
            price = price_tag.get_text(strip=True)
            currency = "€"

            offers.append(
                {
                    "title": title,
                    "url": full_url,
                    "image": image_url,
                    "price": price,
                    "currency": currency,
                }
            )

        if len(offers) >= max_items:
            break

    print(f"Scraping completato. Trovate {len(offers)} offerte.")

    return offers
