from bot_manager import BotManager
from flask import Flask
from threading import Thread
import requests, os

bot = BotManager()

# Start the bot with polling
if __name__ == "__main__":
    print("Starting bot with polling...")
    bot.run()