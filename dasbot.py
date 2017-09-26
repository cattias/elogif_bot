#!/usr/bin/env python
# -*- coding: utf-8 -*-
from uuid import uuid4
import re, json, requests, sys, argparse
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, ParseMode
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import logging
import datetime
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

COUNTER = {}
LAST = {}
LIMIT_PER_USER = 10
TIME_LIMIT = datetime.timedelta(seconds=120)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Salut les moules! Qui veut du boobies ??')


def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='RTFM')

def random(bot, update):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if not COUNTER.get(user_id):
        COUNTER[user_id] = 0
        LAST[user_id] = datetime.datetime.now()
    COUNTER[user_id] += 1
    logger.info("Random boobies asked by '%s %s' (id=%s) for the #%s time in chat room '%s' (id=%s) !" % (update.message.from_user.first_name,
                                                                                                          update.message.from_user.last_name,
                                                                                                          user_id,
                                                                                                          COUNTER[user_id],
                                                                                                          update.message.chat.title,
                                                                                                          chat_id))
    delta = datetime.datetime.now() - LAST[user_id]
    if COUNTER[user_id] > LIMIT_PER_USER and delta < TIME_LIMIT:
        update.message.reply_text("Va te soulager un coup et reviens dans %s secondes ... Bisous Coeur Coeur Love" % (TIME_LIMIT.seconds - delta.seconds))
    else:
        if COUNTER[user_id] > LIMIT_PER_USER and delta >= TIME_LIMIT:
            COUNTER[user_id] = 0
        random_elo = requests.get('http://ns3276663.ip-5-39-89.eu:58080/api/random').json()
        cado = "http://ns3276663.ip-5-39-89.eu/elo-gif/%s" % random_elo['gif']
        LAST[user_id] = datetime.datetime.now()
        bot.send_document(chat_id=chat_id, document=cado)

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))

def main(token):
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("random", random))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    logger.info("start listening ...")
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is Das Bot for Telegram interface with EloGif",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--token', required=True, help='The bot token !')

    options = parser.parse_args()
    main(options.token)