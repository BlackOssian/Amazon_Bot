# main.py – VERSIONE FINALE 5 DICEMBRE 2025 – POSTA SU TELEGRAM SENZA BAN
import os
import time
import logging
import threading
from flask import Flask
from amazon_client import get_offers
from telegram_client import send_offer_photo

# ===================== FLASK PER RENDER FREE 24/7 =====================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Amazon Affiliato FREE 24/7 – Pompa offerte mentre dormi! 💸🔥"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# ===================== LOGGING =====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("amazon_bot.log"),
        logging.StreamHandler()
    ]
)

# ===================== CONFIG =====================
CHECK_INTERVAL = 4 * 60 * 60  # 4 ore
MAX_OFFERS_PER_RUN = 8

posted_urls = set()

def load_posted_urls():
    try:
        with open("posted.txt", "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()

def save_posted_url(url):
    with open("posted.txt", "a", encoding="utf-8") as f:
        f.write(url + "\n")

def run_once():
    logging.info("Inizio scraping Amazon...")
    offers = get_offers(max_items=MAX_OFFERS_PER_RUN * 3)  # ne prendo di più per filtrare

    if not offers:
        logging.error("Nessuna offerta trovata, riprovo tra 4 ore.")
        return

    nuove = 0
    for offer in offers:
        if len(offer["title"]) < 20 or "Offerta Amazon" in offer["title"] or "Viakal" in offer["title"]:  # filtro merda
            continue
        if offer["url"] in posted_urls:
            continue

        try:
            send_offer_photo(offer)
            posted_urls.add(offer["url"])
            save_posted_url(offer["url"])
            nuove += 1
            logging.info(f"Postata: {offer['title'][:60]}... {offer['price']}")
            time.sleep(5)  # ← ANTI-FLOOD: 5 secondi tra un post e l’altro
        except Exception as e:
            logging.error(f"Errore Telegram: {e}")
            time.sleep(10)

        if nuove >= MAX_OFFERS_PER_RUN:
            break

    logging.info(f"Giro finito – {nuove} nuove offerte pubblicate sul canale!")

# ===================== AVVIO =====================
if __name__ == "__main__":
    # Flask per tenere vivo Render FREE
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    port = os.environ.get("PORT", 10000)
    logging.info(f"Flask avviato su porta {port} – FREE 24/7 ATTIVO!")

    logging.info("Bot Amazon affiliato avviato – modalità 24/7")
    posted_urls = load_posted_urls()

    # Primo giro subito
    run_once()

    # Ciclo infinito
    while True:
        try:
            time.sleep(CHECK_INTERVAL)
            run_once()
        except KeyboardInterrupt:
            logging.info("Bot fermato manualmente. Ciao bello!")
            break
        except Exception as e:
            logging.error(f"Errore grave ma continuo: {e}")
            time.sleep(60)
