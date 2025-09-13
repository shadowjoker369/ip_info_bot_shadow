# ======================================================
# 🔥 Telegram Bot - IP Info Lookup (Flask Webhook Version)
# 🚀 Hosted on Render
# 👑 Credit: SHADOW JOKER
# ======================================================

import os
import json
import requests
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
user_data = {}  # Optional if you want to save previous IP lookups

app = Flask(__name__)

# -----------------------------
# Telegram send_message
# -----------------------------
def send_message(chat_id, text, buttons=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }

    if buttons:
        payload["reply_markup"] = json.dumps({"inline_keyboard": buttons})

    try:
        requests.post(API_URL + "sendMessage", json=payload, timeout=5)
    except Exception as e:
        print(f"[✗] send_message error: {e}")

# -----------------------------
# IP Info Lookup
# -----------------------------
def get_ip_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,isp,query,lat,lon"
        resp = requests.get(url, timeout=5).json()
        if resp["status"] == "fail":
            return f"❌ Invalid IP: {resp.get('message', 'Unknown error')}", None

        msg = (
            "╔════════════════════════════╗\n"
            "   🔮 *IP INFORMATION LOOKUP* 🔮\n"
            "╚════════════════════════════╝\n\n"
            f"🆔 *IP*: `{resp['query']}`\n"
            f"🏳 *Country*: {resp['country']}\n"
            f"🏙 *Region*: {resp['regionName']}\n"
            f"🏡 *City*: {resp['city']}\n"
            f"📡 *ISP*: {resp['isp']}\n\n"
            "╔════════════════════════════╗\n"
            "👑 Credit: *SHADOW JOKER*\n"
            "╚════════════════════════════╝"
        )

        buttons = [
            [{"text": "🔍 Check Again", "callback_data": f"check:{resp['query']}"}],
            [
                {"text": "🌐 Whois Lookup", "url": f"https://whois.com/whois/{resp['query']}"},
                {"text": "📍 Google Maps", "url": f"https://www.google.com/maps?q={resp['lat']},{resp['lon']}"}
            ]
        ]

        return msg, buttons
    except Exception as e:
        return f"⚠ Error: {e}", None

# -----------------------------
# Handle Commands
# -----------------------------
def handle_command(message):
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text.startswith("/start"):
        send_message(chat_id, "👋 Welcome to IP Info Bot!\n\nUse `/ip <IP_ADDRESS>` to get details.\n\n👑 Credit: SHADOW JOKER")

    elif text.startswith("/ip"):
        parts = text.split()
        if len(parts) < 2:
            send_message(chat_id, "⚠ Usage: `/ip 8.8.8.8`")
            return
        ip = parts[1]
        info, buttons = get_ip_info(ip)
        send_message(chat_id, info, buttons)

# -----------------------------
# Handle Callback Queries
# -----------------------------
def handle_callback(callback):
    chat_id = callback["message"]["chat"]["id"]
    data = callback["data"]

    if data.startswith("check:"):
        ip = data.split(":", 1)[1]
        info, buttons = get_ip_info(ip)
        # editMessageText API
        payload = {
            "chat_id": chat_id,
            "message_id": callback["message"]["message_id"],
            "text": info,
            "parse_mode": "Markdown",
            "reply_markup": json.dumps({"inline_keyboard": buttons}) if buttons else None
        }
        try:
            requests.post(API_URL + "editMessageText", json=payload, timeout=5)
        except Exception as e:
            print(f"[✗] editMessageText error: {e}")

# -----------------------------
# Flask Routes
# -----------------------------
@app.route("/")
def home():
    return "🤖 IP Info Bot is running!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    if "message" in update:
        handle_command(update["message"])
    elif "callback_query" in update:
        handle_callback(update["callback_query"])
    return "ok"

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
