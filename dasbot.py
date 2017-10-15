#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib3
import threading
urllib3.disable_warnings()

import requests, argparse, uuid
from random import randint
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
VOTE_TIME_LIMIT = datetime.timedelta(seconds=300)
VOTES = {}
GLOBAL_TIMEOUT = 300
URL_ELO = 'http://ns3276663.ip-5-39-89.eu'
PORT_ELO = 58080
URL_ELO_API = '%s:%s/api' % (URL_ELO, PORT_ELO)
URL_ELO_GIF = '%s/elo-gif' % URL_ELO

KATEE = [
    "https://i.imgur.com/TwQWyZ5.mp4",
    "https://media.giphy.com/media/3ov9jIRSrqigFb7vd6/giphy.gif",
    "https://media.giphy.com/media/3o7aD0m6SMTVFwZm3S/giphy.gif",
    "https://media.giphy.com/media/xT9IgBm08DWJElsTD2/giphy.gif",
    "https://media.giphy.com/media/3ohhwfs6xcUWQBVIEo/giphy.gif",
    "https://media.giphy.com/media/l1J9G6uX0fHktGdLG/giphy.gif",
    "https://media.giphy.com/media/3ohhwCNTOIhkGAGlXO/giphy.gif",
    "https://media.giphy.com/media/3ohhwolUdQFoQEV5hm/giphy.gif",
    ]

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Salut les moules! Qui veut du boobies ??', timeout=GLOBAL_TIMEOUT)

def help_command(bot, update):
    logger.info("Help asked by '%s %s' (id=%s)" % (update.message.from_user.first_name, update.message.from_user.last_name, update.message.from_user.id))
    help_text = """
/random si tu veux des boobies random
/rank xx si tu veux les boobies de rang xx
/vote si tu veux proposer un vote !
/stop pour terminer le vote en cours
/next pour terminer le vote en cours et enchainer direct sur un nouveau vote ... parce qu'on est pas là pour niaiser !
/result pour voir les resultats en cours de route
/katee - parce que Katee ...
    """
    bot.send_message(chat_id=update.message.chat_id, text=help_text, timeout=GLOBAL_TIMEOUT)

def _get_boobies(bot, update, command, rank=None, url_boobies=None):
    """
    Internal command to get boobies, either rank or random
    command = 'rank' or 'random'
    """
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if not COUNTER.get(user_id):
        COUNTER[user_id] = 0
        LAST[user_id] = datetime.datetime.now()
    COUNTER[user_id] += 1
    logger.info("Boobies asked by '%s %s' (id=%s) for the #%s time in chat room '%s' (id=%s) !" % (update.message.from_user.first_name,
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
        cado = None
        if url_boobies:
            cado = url_boobies
        else:
            url = '%s/%s' % (URL_ELO_API, command)
            if rank is not None and command == 'rank':
                url = '%s/%s' % (url, rank)
            logger.info("_get_boobies - %s - %s" % (command, url))
            request_elo = requests.get(url).json()
            boobies = None
            if command == 'rank':
                boobies = request_elo[0]['gif']
            else:
                boobies = request_elo['gif']
            cado = "%s/%s" % (URL_ELO_GIF, boobies)
        logger.info("_get_boobies - %s - %s" % (command, cado))
        LAST[user_id] = datetime.datetime.now()
        bot.send_document(chat_id=chat_id, document=cado, timeout=GLOBAL_TIMEOUT)

def random(bot, update):
    """
    Telegram command to get random boobies
    /random
    """
    _get_boobies(bot, update, command='random')

def katee(bot, update):
    """
    Telegram command to get Katee
    /katee /bff
    """
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
    url_boobies = None
    if rank_n:
        url_boobies = KATEE[rank_n % len(KATEE)]
    else:
        url_boobies = KATEE[randint(0, len(KATEE)-1)]
    _get_boobies(bot, update, command="katee", url_boobies=url_boobies)

def rank(bot, update):
    """
    Telegram command to get ranked boobies
    /rank n - n cannot be empty or non integer
    """
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
        _get_boobies(bot, update, command='rank', rank=rank_n)

def vote(bot, update):
    """
    Telegram command to propose a boobies vote
    /vote
    """
    chat_id = update.message.chat_id
    _internal_vote(bot, update.message.from_user.first_name, update.message.from_user.last_name, update.message.from_user.id, chat_id)

def _internal_vote(bot, first_name, last_name, user_id, chat_id):
    """
    Telegram command to propose a boobies vote
    /vote
    """
    logger.info("Vote asked by '%s %s' (id=%s)" % (first_name, last_name, user_id))
    chat_member_count = bot.get_chat_members_count(chat_id)
    global VOTES
    
    if VOTES.get(chat_id) is not None:
        bot.send_message(chat_id=chat_id, text="Y a déjà un vote en cours. Si tu veux lancer un nouveau vote, termine celui là avec /stopvote. Bisous.", timeout=GLOBAL_TIMEOUT)
        return
    
    url = '%s/generate_vote/%s' % (URL_ELO_API, chat_member_count)
    logger.info("vote - %s" % url)
    vote_elo = requests.get(url).json()
    vote_id = str(uuid.uuid4())
    
    boobies_1 = vote_elo['choice_left']
    cado_1 = "%s/%s" % (URL_ELO_GIF, boobies_1)
    logger.info("vote - cado_1 - %s" % cado_1)
    boobies_2 = vote_elo['choice_right']
    cado_2 = "%s/%s" % (URL_ELO_GIF, boobies_2)
    logger.info("vote - cado_2 - %s" % cado_2)

    VOTES[chat_id] = {'id': vote_id, 'vote_elo' : vote_elo, 'votes' : {}, 'choice_left' : 0, 'choice_right' : 0, 'start_time' : datetime.datetime.now()}

    bot.send_message(chat_id=chat_id, text="C'est le moment de voter les coquinous ! (vous avez %s secondes pour voter !)" % VOTE_TIME_LIMIT.seconds, timeout=GLOBAL_TIMEOUT)
    bot.send_message(chat_id=chat_id, text="Boobies #1", timeout=GLOBAL_TIMEOUT)
    bot.send_document(chat_id=chat_id, document=cado_1, timeout=GLOBAL_TIMEOUT)
    bot.send_message(chat_id=chat_id, text="Boobies #2", timeout=GLOBAL_TIMEOUT)
    bot.send_document(chat_id=chat_id, document=cado_2, timeout=GLOBAL_TIMEOUT)

    keyboard = [[InlineKeyboardButton(text="Boobies #1", callback_data="%s|choice_left" % vote_id),
                 InlineKeyboardButton(text="Boobies #2", callback_data="%s|choice_right" % vote_id),
                 InlineKeyboardButton(text="Meh ...", callback_data="%s|meh" % vote_id)]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.send_message(chat_id=chat_id, text='Choisi ton favori:', reply_markup=reply_markup, timeout=GLOBAL_TIMEOUT)

def button(bot, update):
    """
    Telegram button callback for the votes
    """
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    data = query.data.split("|")
    global VOTES

    if VOTES.get(chat_id) is None:
        return

    vote_id = VOTES[chat_id]['id']
    vote_elo = VOTES[chat_id]['vote_elo']
    votes = VOTES[chat_id]['votes']
    
    if len(vote_elo['tokens']) == 0:
        logger.warning("no more tokens to vote ...")
        return
    
    if len(data) == 2:
        if vote_id == data[0]:
            choice = data[1]
            if not user_id in votes.keys():
                token = vote_elo['tokens'].pop()
                if choice == "meh":
                    url = "%s:%s/?id=%s&draw_left=%s&draw_right=%s" % (URL_ELO, PORT_ELO, token, vote_elo['choice_left'], vote_elo['choice_right'])
                else:
                    win = vote_elo[choice]
                    VOTES[chat_id][choice] += 1
                    loose = vote_elo['choice_right'] if choice == 'choice_left' else vote_elo['choice_left']
                    url = "%s:%s/?id=%s&win=%s&loose=%s" % (URL_ELO, PORT_ELO, token, win, loose)
        
                voter = query.from_user.username
                if voter is None:
                    voter = query.from_user.first_name
                text = u"%s a voté !" % voter
                bot.send_message(chat_id=chat_id, text=text, timeout=GLOBAL_TIMEOUT)
        
                logger.info("das_vote_callback - %s - %s" % (voter, url))
                requests.get(url)
                
                VOTES[chat_id]['votes'][user_id] = choice

    if len(vote_elo['tokens']) == 1:
        # == 1 because the bot elogif_bot is counted as 1 in the process and won't vote => assuming it's the only bot in the group too
        logger.info("Everybody has voted ! => next vote !!")
        bot.send_message(chat_id=chat_id, text="Tout le monde il a voté, on passe au suivant !", timeout=GLOBAL_TIMEOUT)
        _internal_stopvote(bot, query.from_user.first_name, query.from_user.last_name, user_id, chat_id)
        _internal_vote(bot, query.from_user.first_name, query.from_user.last_name, user_id, chat_id)

def stopvote(bot, update):
    """
    Telegram command to close a boobies vote
    /stopvote
    """
    _internal_stopvote(bot, update.message.from_user.first_name, update.message.from_user.last_name, update.message.from_user.id, update.message.chat_id)

def _internal_stopvote(bot, first_name, last_name, user_id, chat_id):
    """
    Telegram command to close a boobies vote
    /stopvote
    """
    _internal_result(bot, first_name, last_name, user_id, chat_id)
    global VOTES
    if VOTES.get(chat_id):
        VOTES[chat_id] = None

def result(bot, update):
    """
    Telegram command to see the current results of a boobies vote (without closing it)
    /result
    """
    _internal_result(bot, update.message.from_user.first_name, update.message.from_user.last_name, update.message.from_user.id, update.message.chat_id)

def _internal_result(bot, first_name, last_name, user_id, chat_id):
    """
    Telegram command to see the current results of a boobies vote (without closing it)
    /result
    """
    logger.info("Vote results asked by '%s %s' (id=%s)" % (first_name, last_name, user_id))
    global VOTES
    if VOTES.get(chat_id) is None:
        bot.send_message(chat_id=chat_id, text="Y a pas de vote en cours ...", timeout=GLOBAL_TIMEOUT)
    else:
        vote_elo = VOTES[chat_id]['vote_elo']
        result_left = VOTES[chat_id]['choice_left']
        result_right = VOTES[chat_id]['choice_right']
        
        victory_boobies = None
        if result_left == result_right:
            bot.send_message(chat_id=chat_id, text="Egalité entre les deux (%s votes chacun) ... c'est naze" % result_left, timeout=GLOBAL_TIMEOUT)
            return
        elif result_left > result_right:
            bot.send_message(chat_id=chat_id, text="And the winner is (avec %s votes contre %s):" % (result_left, result_right), timeout=GLOBAL_TIMEOUT)
            victory_boobies = vote_elo['choice_left']
        else:
            bot.send_message(chat_id=chat_id, text="And the winner is (avec %s votes contre %s):" % (result_right, result_left), timeout=GLOBAL_TIMEOUT)
            victory_boobies = vote_elo['choice_right']

        cado = "%s/%s" % (URL_ELO_GIF, victory_boobies)
        logger.info("results - %s" % cado)
        bot.send_document(chat_id=chat_id, document=cado, timeout=GLOBAL_TIMEOUT)

def next_command(bot, update):
    """
    Telegram command to close a boobies vote and propose a new one
    /next
    """
    stopvote(bot, update)
    vote(bot, update)

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))
    if update and update.message and update.message.chat_id:
        bot.send_message(chat_id=update.message.chat_id, text=unicode("ERROR !!!!\n%s" % (error)), timeout=GLOBAL_TIMEOUT)

class CheckOnGoingVotes(threading.Thread):
    def __init__(self, threadID, name, event, bot):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.stopped = event
        self.bot = bot

    def run(self):
        while not self.stopped.wait(5):
            logger.info("Starting " + self.name)
            for chat_id in VOTES.keys():
                if VOTES[chat_id] is not None:
                    if VOTES[chat_id]['start_time'] + VOTE_TIME_LIMIT < datetime.datetime.now():
                        do_next = not VOTES[chat_id]['votes'] == {}
                        text = "Ça niaise trop ..."
                        if do_next:
                            text += " on passe au suivant"
                        self.bot.send_message(chat_id=chat_id, text=text, timeout=GLOBAL_TIMEOUT)
                        try:
                            _internal_stopvote(self.bot, "Das", "Bot", -1, chat_id)
                            if do_next:
                                _internal_vote(self.bot, "Das", "Bot", -1, chat_id)
                        except Exception, ex:
                            logger.warning("Error : %s" % str(ex))

def main(token):
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("random", random))
    dp.add_handler(CommandHandler("rank", rank))
    dp.add_handler(CommandHandler("vote", vote))
    dp.add_handler(CommandHandler("next", next_command))
    dp.add_handler(CommandHandler(["stopvote", "stop"], stopvote))
    dp.add_handler(CommandHandler("result", result))
    dp.add_handler(CommandHandler(["katee", "bff"], katee))
    dp.add_handler(CallbackQueryHandler(button))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    logger.info("start listening ...")
    updater.start_polling()

    stopFlag = threading.Event()
    thread = CheckOnGoingVotes(1, "VoteChecker", stopFlag, updater.bot)
    thread.start()

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