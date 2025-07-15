import html

from telebot import TeleBot
import os
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from api_manager import ApiManager
load_dotenv()

CHAT_ID = os.getenv("CHAT_ID")

# todo: show a message when bot is downloading the song, then delete the message once the song has completed downloading

class BotManager:
    def __init__(self):
        self.bot = TeleBot(token=os.getenv("BOT_TOKEN"))
        self.yt_searcher = ApiManager()
        self.user_state = {}
        self.user_last_message = {}

        self.bot.message_handler(commands=['start'])(self.start)
        self.bot.message_handler(commands=['search'])(self.search_music)
        self.bot.message_handler(func=lambda message: CHAT_ID in self.user_state and self.user_state[CHAT_ID] == "waiting_for_song")(self.process_search_query)
        self.bot.callback_query_handler(func=lambda call: True)(self.process_calls)
        # note the callback_query_handler must have a function, and must accept the call, so to make the bot process all calls we just make the function output True everytime

    def run(self):
        self.bot.polling()

    def start(self, message):
        self.bot.send_message(chat_id=CHAT_ID, text="🎵 Welcome! Enter /search to start searching for songs.")

    def search_music(self, message):
        self.bot.send_message(chat_id=CHAT_ID, text="🔎 Please enter the song name:")
        # change user state to 'searching song'
        self.user_state[CHAT_ID] = "waiting_for_song"

    # using .pop() on a list means removes an element at a particular index, eg. .pop(index), using .pop() on dictionary
    # means remove the element but you put the key inside, eg. .pop(key)

    def process_search_query(self, message):
        query = message.text
        self.user_state.pop(CHAT_ID) # this removes the key from the self.user_state dictionary, effectively removing the value as well
        results = self.yt_searcher.search(query=query)
        markup = InlineKeyboardMarkup()

        for result in results:
            button = InlineKeyboardButton(text=html.unescape(result['video_title']), callback_data=result["video_id"])
            markup.add(button)

        song_list_msg = self.bot.send_message(CHAT_ID, "Choose a song: ", reply_markup=markup)
        self.user_last_message[CHAT_ID] = song_list_msg.message_id

    def process_calls(self, call):#instead of message, now we just process the call
        download_in_progress_msg = self.bot.send_message(CHAT_ID, "Download in progress... ⏳")
        self.bot.delete_message(CHAT_ID, self.user_last_message[CHAT_ID])

        # Add the newly sent message to the last message
        self.user_last_message[CHAT_ID] = download_in_progress_msg.message_id

        video_id = call.data
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        file_path = self.yt_searcher.download_song(url=youtube_url).replace(".webm", ".mp3")
        song_info = self.yt_searcher.get_song_info(url=youtube_url)
        try:
            with open(file_path, "rb") as song:
                # telegram reads audio files in binary mode, hence rb.
                self.bot.send_audio(CHAT_ID, audio=song, performer=song_info['title'], title=song_info['title'], timeout=300)
                # open the mp3 file downloaded on computer and then send this file to telegram. make sure to include
                # performer and title details so the audio shows up properly on telegram
        except Exception as e:
            # Remove the last message
            self.bot.delete_message(CHAT_ID, self.user_last_message[CHAT_ID])
            self.bot.send_message(CHAT_ID, f"❌ Error encountered when downloading bot. Please try again: {e}")

        self.bot.send_message(CHAT_ID, "Downloaded song. Enjoy! 🎉")
        # Remove the last message
        self.bot.delete_message(CHAT_ID, self.user_last_message[CHAT_ID])

        if os.path.exists(file_path):
            # os is a module, path is a SUB-module inside the os module. .exists() is a function, which checks if the file path exists or not
            os.remove(file_path)