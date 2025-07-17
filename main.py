from bot_manager import BotManager
from flask import Flask
from threading import Thread
import requests, os
import imageio_ffmpeg

ffmpeg_binary = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["PATH"] = os.path.dirname(ffmpeg_binary) + os.pathsep + os.environ["PATH"]

bot = BotManager()

# Start the bot with polling
if __name__ == "__main__":
    print("Starting bot with polling...")
    bot.run()