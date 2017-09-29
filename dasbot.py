#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib3
urllib3.disable_warnings()

import requests, argparse, uuid
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import logging
import datetime
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

COUNTER = {}
LAST = {}
LIMIT_PER_USER = 10
TIME_LIMIT = datetime.timedelta(seconds=60)
VOTES = None

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Salut les moules! Qui veut du boobies ??')


def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='/random si tu veux des boobies random\n/rank xx si tu veux les boobies de rang xx\n/vote si tu veux voter !\n/stopvote pour terminer le vote en cours')

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

def rank(bot, update):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if not COUNTER.get(user_id):
        COUNTER[user_id] = 0
        LAST[user_id] = datetime.datetime.now()
    COUNTER[user_id] += 1
    rank_n = 0
    if update.message.text:
        split = update.message.text.split(" ")
        if len(split) > 1:
            le_rank = split[1]
        else:
            le_rank = None
        try:
            rank_n = int(le_rank)
        except:
            pass
    if rank_n == 0:
        update.message.reply_text("Demande moi un rang comme il faut baltringue ... /rank 1 par exemple ...")
    else:    
        logger.info("Boobies #%s asked by '%s %s' (id=%s) for the #%s time in chat room '%s' (id=%s) !" % (rank_n,
                                                                                                           update.message.from_user.first_name,
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
            rank_elo = requests.get('http://ns3276663.ip-5-39-89.eu:58080/api/rank/%s' % rank_n).json()
            cado = "http://ns3276663.ip-5-39-89.eu/elo-gif/%s" % rank_elo[0]['gif']
            LAST[user_id] = datetime.datetime.now()
            bot.send_document(chat_id=chat_id, document=cado)

def vote(bot, update):
    chat_id = update.message.chat_id
    chat_member_count = bot.get_chat_members_count(chat_id)
    global VOTES
    
    if VOTES is not None:
        bot.send_message(chat_id=chat_id, text="Y a déjà un vote en cours. Si tu veux lancer un nouveau vote, termine celui là avec /stopvote. Bisous.")
        return
    
    url = 'http://ns3276663.ip-5-39-89.eu:58080/api/generate_vote/%s' % chat_member_count
    logger.info(url)
    vote_elo = requests.get(url).json()
    # vote_id = str(uuid.uuid4())
    
    boobies_1 = vote_elo['choice_left']
    cado_1 = "http://ns3276663.ip-5-39-89.eu/elo-gif/%s" % boobies_1
    boobies_2 = vote_elo['choice_right']
    cado_2 = "http://ns3276663.ip-5-39-89.eu/elo-gif/%s" % boobies_2

    VOTES = {'vote_elo' : vote_elo, 'votes' : {}, 'choice_left' : 0, 'choice_right' : 0}

    bot.send_message(chat_id=chat_id, text="C'est le moment de voter les coquinous !")

    bot.send_message(chat_id=chat_id, text="Boobies #1")
    bot.send_document(chat_id=chat_id, document=cado_1)
    bot.send_message(chat_id=chat_id, text="Boobies #2")
    bot.send_document(chat_id=chat_id, document=cado_2)

    keyboard = [[InlineKeyboardButton(text="Boobies #1", callback_data="choice_left"),
                 InlineKeyboardButton(text="Boobies #2", callback_data="choice_right"),
                 InlineKeyboardButton(text="Meh ...", callback_data="meh")]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.send_message(chat_id=chat_id, text='Choisi ton favori:', reply_markup=reply_markup)

def button(bot, update):
    query = update.callback_query
    user_id = query.from_user.id
    choice = query.data
    global VOTES

    if VOTES is None:
        return

    vote_elo = VOTES['vote_elo']
    votes = VOTES['votes']
    
    if not user_id in votes.keys():
        token = vote_elo['tokens'].pop()
        if choice == "meh":
            url = "http://ns3276663.ip-5-39-89.eu:58080/?id=%s&draw_left=%s&draw_right=%s" % (token, vote_elo['choice_left'], vote_elo['choice_right'])
        else:
            win = vote_elo[choice]
            VOTES[choice] += 1
            loose = vote_elo['choice_right'] if choice == 'choice_left' else vote_elo['choice_left']
            url = "http://ns3276663.ip-5-39-89.eu:58080/?id=%s&win=%s&loose=%s" % (token, win, loose)

        text = u"%s a voté !" % query.from_user.username
        bot.send_message(chat_id=query.message.chat_id, text=text)

        logger.info(url)
        requests.get(url)
        
        VOTES['votes'][user_id] = choice

def stopvote(bot, update):
    chat_id = update.message.chat_id
    global VOTES
    if VOTES is None:
        bot.send_message(chat_id=chat_id, text="Y a pas de vote en cours ...")
    else:
        vote_elo = VOTES['vote_elo']
        result_left = VOTES['choice_left']
        result_right = VOTES['choice_right']
        
        victory_boobies = None
        if result_left == result_right:
            bot.send_message(chat_id=chat_id, text="Egalité entre les deux (%s votes chacun) ... c'est naze" % result_left)
            VOTES=None
            return
        elif result_left > result_right:
            bot.send_message(chat_id=chat_id, text="And the winner is (avec %s votes contre %s):" % (result_left, result_right))
            victory_boobies = vote_elo['choice_left']
        else:
            bot.send_message(chat_id=chat_id, text="And the winner is (avec %s votes contre %s):" % (result_right, result_left))
            victory_boobies = vote_elo['choice_right']

        cado = "http://ns3276663.ip-5-39-89.eu/elo-gif/%s" % victory_boobies
        bot.send_document(chat_id=chat_id, document=cado)
  
        VOTES=None

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
    dp.add_handler(CommandHandler("rank", rank))
    dp.add_handler(CommandHandler("vote", vote))
    dp.add_handler(CommandHandler("stopvote", stopvote))
    dp.add_handler(CallbackQueryHandler(button))

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