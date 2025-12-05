# telegram_client.py – VERSIONE CHE FUNZIONA DAVVERO 2025 (async + Application)
import os
import logging
from telegram import Bot
from telegram.constants import ParseMode

# Configurazione del logging (da aggiungere all'inizio del file)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
# ... il resto del tuo codice

# Token e chat da env (funziona con @username se bot è admin)
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "@superamaz0n")

bot = Bot(token=TOKEN)

async def send_offer_async(offer):
    caption = (
        f"<b>{offer['title']}</b>\n"
        f"💰 <b>Prezzo:</b> {offer['price']} {offer['currency']}\n"
        f"🔗 <a href=\"{offer['url']}\">Vai all'offerta su Amazon</a>"
    )

    try:
        await bot.send_photo(
            chat_id=CHAT_ID,
            photo=offer["image"],
            caption=caption,
            parse_mode=ParseMode.HTML,
            read_timeout=30,
            write_timeout=30,
            connect_timeout=30,
            pool_timeout=30
        )
        logging.info(f"✅ POSTATA SU {CHAT_ID}: {offer['title'][:60]}...")
    except Exception as e:
        logging.error(f"❌ ERRORE TELEGRAM: {e}")

import asyncio # Assicurati che asyncio sia importato

def send_offer_photo(offer):
    """Esegue l'invio asincrono in modo sincrono usando asyncio.run()"""
    try:
        # Questo crea, esegue e chiude un loop pulito per il singolo task
        asyncio.run(send_offer_async(offer))
    except RuntimeError as e:
        # Gestisce i casi in cui l'invio viene chiamato in un contesto già in esecuzione
        if 'Event loop is closed' in str(e):
             logging.warning("⚠️ Tentativo di invio fallito a causa di loop chiuso. Saltato.")
        else:
             logging.error(f"❌ ERRORE ASYNCIO GENERALE: {e}")
    except Exception as e:
        # Errori generici di invio che non sono catturati in send_offer_async
        logging.error(f"❌ ERRORE NELLA CHIAMATA SYNC: {e}")
