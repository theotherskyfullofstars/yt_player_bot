from bot_manager import BotManager
from flask import Flask
from threading import Thread
import requests, os

bot = BotManager()
app = Flask(__name__)

# Optional root route for confirmation
@app.route("/")
def home():
    return "Bot is running with polling."

@app.route("/test-telegram")
def test_telegram():
    token = os.getenv("TOKEN")  # Replace with your bot token
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return f"Telegram API is reachable: {response.json()}", 200
    except requests.exceptions.RequestException as e:
        return f"Error reaching Telegram API: {e}", 500

# Start the bot with polling
if __name__ == "__main__":
    print("Starting bot with polling...")
    bot_thread = Thread(target=bot.run)
    bot_thread.start()

    # Start Flask app to satisfy Render's port requirement
    app.run(port=5001) # note that this line is blocking, and will keep the main process alive, so there is no need to run
    # bot_thread.join()
    # the host="0.0.0.0" tells flask to accept requests from any ip address, not just local machines
    # disable debug_mode (unlike previous website projects)
    # because telegram can only have 1 bot instance running, but when i set debug mode to true, it runs the script twice, 1 to detect for changes, 1 to host the website, but this creates 2 bot instance when creates the telegram error?
