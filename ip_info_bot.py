#!/usr/bin/env python3
import os
import logging
import requests
from ipaddress import ip_address

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# -------- CONFIG ----------
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Render env var থেকে নিবে

IP_API_URL = "http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,zip,lat,lon,timezone,isp,org,as,query,reverse,proxy,mobile,hosting"
MAPS_LINK = "https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=10/{lat}/{lon}"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def query_ip(ip: str) -> dict:
    try:
        r = requests.get(IP_API_URL.format(ip=ip), timeout=8)
        return r.json()
    except Exception:
        return {"status": "fail", "message": "API request error"}


def pretty(data: dict) -> str:
    if data.get("status") != "success":
        return f"❌ <b>Error:</b> {data.get('message','Unknown')}"

    return (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🛰️ <b>SHADOW JOKER IP INFO</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔹 <b>IP:</b> <code>{data['query']}</code>\n"
        f"🌍 <b>Location:</b>\n   {data['city']}, {data['regionName']}, {data['country']} ({data['zip']})\n"
        f"📍 <b>Coordinates:</b>\n   {data['lat']}, {data['lon']}\n"
        f"⏰ <b>Timezone:</b>\n   {data['timezone']}\n"
        f"🏢 <b>ISP:</b>\n   {data['isp']}\n"
        f"🏷️ <b>Org:</b>\n   {data['org']}\n"
        f"🛰️ <b>ASN:</b>\n   {data['as']}\n\n"
        f"🌐 <a href='{MAPS_LINK.format(lat=data['lat'], lon=data['lon'])}'>📌 View on Map</a>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ <i>Powered by SHADOW JOKER</i>\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ip = update.message.text.strip()
    try:
        ip_address(ip)  # valid কিনা চেক করবে
    except Exception:
        await update.message.reply_text("⚠️ Please send a valid IP address.")
        return

    data = query_ip(ip)
    await update.message.reply_text(
        pretty(data),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("⚠️ TELEGRAM_BOT_TOKEN environment variable not set!")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("✅ Bot started (Professional Box Style)")
    app.run_polling()


if __name__ == "__main__":

    main()

