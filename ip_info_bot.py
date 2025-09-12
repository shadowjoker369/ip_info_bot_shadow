import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# =========================
# Bot Token (Render Env Variable থেকে নাও অথবা সরাসরি বসাও)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")

# Render এর PORT (Render দেয়, fallback = 8080)
PORT = int(os.getenv("PORT", 8080))
# =========================


# ----------- Commands -----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "**👋 Welcome to IP Info Bot!**\n\n"
        "🔍 শুধু একটা *IP Address* পাঠাও, আমি বিস্তারিত বলব।\n\n"
        "📌 উদাহরণ: `8.8.8.8`\n\n"
        "**💡 Developer:** @YourUsername",
        parse_mode="Markdown"
    )


async def ip_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ip = update.message.text.strip()
    url = f"http://ip-api.com/json/{ip}?fields=status,message,query,country,regionName,city,isp,org,as,timezone,lat,lon"
    data = requests.get(url).json()

    if data["status"] == "fail":
        await update.message.reply_text("❌ *ভুল IP Address দেওয়া হয়েছে!*", parse_mode="Markdown")
        return

    response = (
        "**🌍 IP Address Information**\n\n"
        f"🔹 **IP:** `{data['query']}`\n"
        f"🏳 **Country:** {data['country']}\n"
        f"🏙 **Region:** {data['regionName']}\n"
        f"🌆 **City:** {data['city']}\n"
        f"⏰ **Timezone:** {data['timezone']}\n"
        f"📡 **ISP:** {data['isp']}\n"
        f"🏢 **Org:** {data['org']}\n"
        f"⚡ **AS:** {data['as']}\n"
        f"📍 **Location:** {data['lat']}, {data['lon']}\n\n"
        "━━━━━━━━━━━━━━━\n"
        "**👨‍💻 Credit:** @YourUsername"
    )

    await update.message.reply_text(response, parse_mode="Markdown")


# ----------- Main -----------

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ip_lookup))

    # Webhook Mode
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}"
    )


if __name__ == "__main__":
    main()
