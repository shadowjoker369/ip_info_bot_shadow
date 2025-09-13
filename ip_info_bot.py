# ======================================================
# 🔥 Telegram Bot - IP Info Lookup
# 🚀 Hosted on Render with Webhook
# 👑 Credit: **SHADOW JOKER**
# ======================================================

import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)

# -----------------------------
# BOT CONFIG
# -----------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
PORT = int(os.getenv("PORT", 8443))
HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")

# -----------------------------
# IP Lookup Function
# -----------------------------
def get_ip_info(ip: str) -> tuple[str, InlineKeyboardMarkup | None]:
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,isp,query,lat,lon"
        response = requests.get(url, timeout=5).json()

        if response["status"] == "fail":
            return f"❌ Invalid IP: {response.get('message', 'Unknown error')}", None

        msg = (
            "╔════════════════════════════╗\n"
            "   🔮 *IP INFORMATION LOOKUP* 🔮\n"
            "╚════════════════════════════╝\n\n"
            f"🆔 *IP*: `{response['query']}`\n"
            f"🏳 *Country*: {response['country']}\n"
            f"🏙 *Region*: {response['regionName']}\n"
            f"🏡 *City*: {response['city']}\n"
            f"📡 *ISP*: {response['isp']}\n\n"
            "╔════════════════════════════╗\n"
            "👑 Credit: *SHADOW JOKER*\n"
            "╚════════════════════════════╝"
        )

        # --- Inline Keyboard ---
        buttons = [
            [InlineKeyboardButton("🔍 Check Again", callback_data=f"check:{response['query']}")],
            [
                InlineKeyboardButton("🌐 Whois Lookup", url=f"https://whois.com/whois/{response['query']}"),
                InlineKeyboardButton("📍 Google Maps", url=f"https://www.google.com/maps?q={response['lat']},{response['lon']}")
            ]
        ]
        keyboard = InlineKeyboardMarkup(buttons)

        return msg, keyboard

    except Exception as e:
        return f"⚠ Error: {e}", None

# -----------------------------
# Bot Commands
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to IP Info Bot!\n\n"
        "Use the command:\n"
        "`/ip <IP_ADDRESS>` to get details.\n\n"
        "👑 Credit: **SHADOW JOKER**",
        parse_mode="Markdown"
    )

async def ip_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠ Usage: `/ip 8.8.8.8`", parse_mode="Markdown")
        return

    ip = context.args[0]
    info, keyboard = get_ip_info(ip)

    await update.message.reply_text(
        info,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# -----------------------------
# Callback Handler (Check Again)
# -----------------------------
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("check:"):
        ip = query.data.split(":", 1)[1]
        info, keyboard = get_ip_info(ip)
        await query.edit_message_text(
            text=info,
            parse_mode="Markdown",
            reply_markup=keyboard
        )

# -----------------------------
# MAIN APP
# -----------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ip", ip_lookup))
    app.add_handler(CallbackQueryHandler(button_click))

    # ✅ Webhook mode (Render এ কাজ করবে)
    if HOSTNAME:
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=f"https://{HOSTNAME}/{BOT_TOKEN}",
        )
    else:
        # ✅ লোকাল টেস্টের জন্য polling
        app.run_polling()

if __name__ == "__main__":
    main()
