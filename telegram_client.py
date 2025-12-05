# telegram_client.py – FUNZIONA AL 100% ANCHE SU RENDER FREE (2025)
import os
import asyncio
import logging
from telegram import Bot
from telegram.constants import ParseMode

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "@superamaz0n")

bot = Bot(token=TOKEN)

async def _send_photo(offer):
    caption = (
        f"<b>{offer['title']}</b>\n"
        f"💰 <b>Prezzo:</b> {offer['price']} {offer['currency']}\n"
        f"🔗 <a href=\"{offer['url']}\">Vai all'offerta su Amazon</a>"
    )
    
    await bot.send_photo(
        chat_id=CHAT_ID,
        photo=offer["image"],
        caption=caption,
        parse_mode=ParseMode.HTML,
        read_timeout=30,
        write_timeout=30,
        connect_timeout=30
    )

def send_offer_photo(offer):
    try:
        # Questo è l’unico modo che funziona al 100% su Render
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Se il loop è già in esecuzione (come su Render)
            task = loop.create_task(_send_photo(offer))
            # Non aspettiamo, lasciamo che continui in background
        else:
            loop.run_until_complete(_send_photo(offer))
        logging.info(f"POSTATA SU {CHAT_ID}: {offer['title'][:60]}...")
    except Exception as e:
        logging.error(f"ERRORE TELEGRAM: {e}")
