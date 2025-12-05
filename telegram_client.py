# telegram_client.py – VERSIONE CHE FUNZIONA DAVVERO 2025 (async + Application)
import os
import logging
from telegram import Bot
from telegram.constants import ParseMode

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

def send_offer_photo(offer):
    import asyncio
    # Crea un loop dedicato per ogni messaggio (funziona sempre)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(send_offer_async(offer))
    finally:
        loop.close()
