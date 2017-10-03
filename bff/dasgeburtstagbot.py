#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib3
import threading
urllib3.disable_warnings()

import argparse
from telegram.ext import Updater, CommandHandler
import logging
import datetime
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

GLOBAL_TIMEOUT = 300

BFF_EASTER_EGG = [
    "https://i.imgur.com/TwQWyZ5.mp4",
    "https://media.giphy.com/media/xIbB8NhP41B7y/giphy.gif",
    "https://media.giphy.com/media/am3dOgmvxPVRK/giphy.gif",
    "https://media.giphy.com/media/L3QKN7NivNw2s/giphy.gif",
    "https://media.giphy.com/media/bkMe1unjI3i2Q/giphy.gif",
    "https://media.giphy.com/media/SQjyCcsqTTXeU/giphy.gif",
    "https://media.giphy.com/media/P1BmuAFbE8lmU/giphy.gif",
    "https://media.giphy.com/media/PObzLcJMf87VC/giphy.gif",
    "https://media.giphy.com/media/Kg17Yw7L9eJ1e/giphy.gif",
    "https://media.giphy.com/media/3o6YfTOZtmgiNz6Tfy/giphy.gif",
    "https://media.giphy.com/media/gFdReYOaEvMuQ/giphy.gif",
    "https://media.giphy.com/media/sjdbYwvERRi1i/giphy.gif",
    "https://media.giphy.com/media/KNj9rHJv7PNDi/giphy.gif",
    "https://media.giphy.com/media/b5iO1KtQpTkxq/giphy.gif",
    "https://media.giphy.com/media/l0He2qi0EGY5y4HZK/giphy.gif",
    "https://media.giphy.com/media/qpnjSTdNg0gBG/giphy.gif",
    "http://ns3276663.ip-5-39-89.eu/elo-gif/1eeef8fe84098a08dc81d21c8519769bd9af0ce6.gif",
    "http://ns3276663.ip-5-39-89.eu/elo-gif/2MRvnqK.gif.jpg",
    "http://ns3276663.ip-5-39-89.eu/elo-gif/4f9f6c2dc154697040f8281f36fe63766ecded3c.gif",
    "http://ns3276663.ip-5-39-89.eu/elo-gif/ibiDVGoA2o4PXN.gif",
    "http://ns3276663.ip-5-39-89.eu/elo-gif/1366907760-1366904520158.gif",
    "http://ns3276663.ip-5-39-89.eu/elo-gif/1366907760-1366904392969.gif",
    "http://ns3276663.ip-5-39-89.eu/elo-gif/6483102t6wm.gif",
    "http://ns3276663.ip-5-39-89.eu/elo-gif/ceb7618f6fe4f3ca9ac9780731c48b84a705604f.gif",
    ]
BFF_EASTER_EGG_LAST = None
ROOM_ID = -299669831
INDEX = 0
START_DATE = datetime.datetime(2017,10,11)
INTERVAL_SEND = datetime.timedelta(minutes=10)

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Salut BFF. Ceci est un Bot pour ton anniversaire ! Spécial Kate(e) !', timeout=GLOBAL_TIMEOUT)

def help_command(bot, update):
    logger.info("Help asked by '%s %s' (id=%s) in room %s" % (update.message.from_user.first_name, update.message.from_user.last_name, update.message.from_user.id, update.message.chat_id))
    help_text = """Rien à faire. C'est un bot magique."""
    bot.send_message(chat_id=update.message.chat_id, text=help_text, timeout=GLOBAL_TIMEOUT)

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))
    if update and update.message and update.message.chat_id:
        bot.send_message(chat_id=update.message.chat_id, text=unicode("Putain t'as tout pété !\n%s" % (error)), timeout=GLOBAL_TIMEOUT)

def when_is_the_next(bot, update):
    logger.info("When is the next asked by '%s %s' (id=%s) in room %s" % (update.message.from_user.first_name, update.message.from_user.last_name, update.message.from_user.id, update.message.chat_id))
    now = datetime.datetime.now()
    if now.date() < START_DATE.date():
        bot.send_message(chat_id=update.message.chat_id, text="Patience ... ça arrive !", timeout=GLOBAL_TIMEOUT)
    elif now.date() > START_DATE.date():
        bot.send_message(chat_id=update.message.chat_id, text="C'est fini ... va falloir attendre l'année prochaine ! Bisous.", timeout=GLOBAL_TIMEOUT)
    else:
        global BFF_EASTER_EGG_LAST
        if BFF_EASTER_EGG_LAST:
            bot.send_message(chat_id=update.message.chat_id, text="Prochain cadeau dans %s minutes" % (int((BFF_EASTER_EGG_LAST+INTERVAL_SEND-now).seconds)/60), timeout=GLOBAL_TIMEOUT)

class DasBFFThread(threading.Thread):
    def __init__(self, threadID, name, event, bot):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.stopped = event
        self.bot = bot

    def run(self):
        global INDEX
        global BFF_EASTER_EGG_LAST
        if INDEX is None:
            INDEX = 0
        while not self.stopped.wait(10):
            logger.info("Starting " + self.name)
            now = datetime.datetime.now()
            if now.day == START_DATE.day and now.month == START_DATE.month:
                if not BFF_EASTER_EGG_LAST or BFF_EASTER_EGG_LAST+INTERVAL_SEND < now:
                    logger.info("Sending cado to BFF")
                    random_kate = INDEX
                    logger.info(BFF_EASTER_EGG[random_kate])
                    try:
                        self.bot.send_message(ROOM_ID, "Cadeau pour mon BFF !! Joyeux anniversaire <3 <3", timeout=GLOBAL_TIMEOUT)
                        self.bot.send_document(ROOM_ID, BFF_EASTER_EGG[random_kate], timeout=GLOBAL_TIMEOUT)
                    except:
                        logger.warning("Fail : %s" % random_kate)                            
                        self.bot.send_message(ROOM_ID, "Fail : %s - %s" % (random_kate, BFF_EASTER_EGG[random_kate]), timeout=GLOBAL_TIMEOUT)
                    INDEX += 1
                    BFF_EASTER_EGG_LAST = now
                    if INDEX == len(BFF_EASTER_EGG):
                        INDEX = 0

def main(token, room_id):
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)
    global ROOM_ID
    ROOM_ID = -int(room_id)
    logger.info("Select room id : %s" % ROOM_ID)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("when", when_is_the_next))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    logger.info("start listening ...")
    updater.start_polling()

    stopFlag = threading.Event()
    thread = DasBFFThread(1, "BFFChecker", stopFlag, updater.bot)
    thread.start()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is Das Bot für mein BFF",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--token', required=True, help='The bot token !')
    # Room QA 2 : -180718229
    # Room BFF : -299669831
    parser.add_argument('--room', required=True, help='The room id !')

    options = parser.parse_args()
    main(options.token, options.room)