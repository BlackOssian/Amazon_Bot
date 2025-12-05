# main.py – VERSIONE CON FILTRO CATEGORIA ESPLICITO
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
    # use_reloader=False è necessario in un ambiente multi-thread come Render
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

# ===================== CONFIG & FILTRI =====================
CHECK_INTERVAL = 4 * 60 * 60  # 4 ore (4 ore * 60 minuti * 60 secondi)
MAX_POSTS_PER_RUN = 8        # Massimo post per ciclo

posted_urls = set()

# ----------------- FILTRO CATEGORIE -----------------
# 1. MAPPATURA: Definisci la tua Categoria (chiave) e le parole chiave associate (valori)
# Il sistema assegnerà l'offerta alla prima categoria che trova nel titolo.
CATEGORY_MAPPING = {
    "elettronica": ["mouse", "tastiera", "cuffie", "scheda video", "ssd", "telecomando", "smartwatch", "tv", "monitor"],
    "gaming": ["ps5", "xbox", "nintendo", "gioco", "joypad", "logitech", "razer"],
    "casa_giardino": ["tappeto", "aspirapolvere", "trapano", "luci led", "sedia ufficio", "martello", "utensile", "giardino"],
    "abbigliamento": ["scarpe", "giacca", "maglione", "t-shirt", "pantaloni", "camicia"],
    "cura_persona": ["rasoio", "profumo", "crema", "spazzolino elettrico", "massaggiatore"],
    # Categoria di esclusione esplicita per i prodotti a basso margine che intasano il feed
    "esclusi_generici": ["viakal", "disincrostante", "lavatrice", "detersivo", "candeggina", "alimento", "cibo", "sapone"]
}

# 2. SELEZIONE: Inserisci QUI le categorie che VUOI PUBBLICARE.
# Solo le offerte che rientrano in queste categorie verranno processate.
# Nota: La categoria "esclusi_generici" viene sempre scartata.
ALLOWED_CATEGORIES = ["elettronica", "gaming", "casa_giardino"]
# ----------------------------------------------------------------------


def categorize_offer(title):
    """Assegna una categoria all'offerta in base alle parole chiave nel titolo."""
    title_lower = title.lower()
    for category, keywords in CATEGORY_MAPPING.items():
        for keyword in keywords:
            if keyword in title_lower:
                return category
    return "altro" # Se nessuna keyword corrisponde, assegna la categoria 'altro'

# ===================== GESTIONE URL PUBBLICATI =====================
def load_posted_urls():
    try:
        with open("posted.txt", "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()

def save_posted_url(url):
    with open("posted.txt", "a", encoding="utf-8") as f:
        f.write(url + "\n")

# ===================== FUNZIONE PRINCIPALE =====================
def run_once():
    global posted_urls
    logging.info("Inizio scraping Amazon...")
    
    # Prende molte più offerte per avere un pool da filtrare
    offers = get_offers(max_items=MAX_POSTS_PER_RUN * 10) 

    if not offers:
        logging.error("Nessuna offerta trovata, riprovo tra 4 ore.")
        return

    nuove = 0
    
    for offer in offers:
        
        # 1. CATEGORIZZAZIONE DELL'OFFERTA
        category = categorize_offer(offer["title"])

        # 2. FILTRO ESCLUSIONE ESPLICITA (BLACKLIST)
        if category == "esclusi_generici":
            logging.info(f"SALTATA (Esclusa): {offer['title'][:60]}... Categoria: {category}")
            continue

        # 3. FILTRO DI INCLUSIONE (WHITELIST)
        if ALLOWED_CATEGORIES and category not in ALLOWED_CATEGORIES:
            logging.info(f"SALTATA (Non Autorizzata): {offer['title'][:60]}... Categoria: {category}")
            continue
            
        # 4. FILTRO PER URL GIA' PUBBLICATO
        if offer["url"] in posted_urls:
            continue
            
        # 5. LIMITAZIONE NUMERO MASSIMO POST
        if nuove >= MAX_POSTS_PER_RUN:
            break
            
        # 6. POSTING E REGISTRAZIONE
        try:
            # Invio foto e messaggio a Telegram
            send_offer_photo(offer) 
            
            # Aggiornamento stato
            posted_urls.add(offer["url"])
            save_posted_url(offer["url"])
            nuove += 1
            
            time.sleep(10)  # ANTI-FLOOD ESTREMO
            
        except Exception as e:
            # Se il post fallisce, logga e continua con la prossima offerta
            logging.error(f"Errore durante il posting di {offer['url']}: {e}")

    logging.info(f"Giro finito – {nuove} nuove offerte pubblicate sul canale!")

# ===================== AVVIO PRINCIPALE =====================
if __name__ == "__main__":
    # Avvio Flask su un thread separato
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    port = os.environ.get("PORT", 10000)
    logging.info(f"Flask avviato su porta {port} – FREE 24/7 ATTIVO!")

    logging.info("Bot Amazon affiliato avviato – modalità 24/7")
    posted_urls = load_posted_urls()

    # Primo giro subito
    run_once()

    # Ciclo infinito per l'intervallo
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
