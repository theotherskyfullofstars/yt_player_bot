from bot_manager import BotManager
from flask import Flask, request
import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/{TOKEN}"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

bot_manager = BotManager()
bot = bot_manager.bot
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running with webhook.", 200

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    json_str = request.stream.read().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    print(f"Update received: {update}")
    bot.process_new_updates([update])
    print("Bot processed update.")
    return "", 200

if __name__ == "__main__":
    print("Setting up webhook...")
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(port=5001, debug=False)