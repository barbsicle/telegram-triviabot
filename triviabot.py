"""
SHING'S TELEGRAM TRIVIA BOT
Usage: A bot that posts WoW trivia questions.
Gives a short timer and checks for correct answers.
TODO: Keep score, Adjust settings, Identifier per group chat
"""


import telegram
from random import randint
from threading import Timer
from time import sleep
import logging


# Enable Logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)

# We use this var to save the last chat id, so we can reply to it, and the var chat to store all known chats.
last_chat_id = 0
chat = []


# Define vars for the bot.
created = {}
change = {}
changing = {}
trivia_in_session = {}
trivia_await_answer = {}
trivia_timer = {}
time_between_questions = {}
session_length = {}
qnfile = {}
qn = {}
ans1 = {}
ans = {}
bank = {}
score = {}
i = {}
n = {}
attempt = {}
topscorer = {}
t1 = {}
t2 = {}


# Define a few (command) handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    last_chat_id = update.message.chat_id
    if not (last_chat_id in created):
        created[last_chat_id] = True
        print('[DEBUG] First time user/chat. Chat ID is ' + str(last_chat_id) + '. Setting variables....')
        change[last_chat_id] = False
        changing[last_chat_id] = 0
        trivia_in_session[last_chat_id] = False
        trivia_await_answer[last_chat_id] = False
        trivia_timer[last_chat_id] = 20
        time_between_questions[last_chat_id] = 3
        session_length[last_chat_id] = 5
        qnfile[last_chat_id] = 'questions_wow'
        qn[last_chat_id] = ''
        ans1[last_chat_id] = []
        ans[last_chat_id] = []
        bank[last_chat_id] = {}
        score[last_chat_id] = {}
        print('[DEBUG] Variables set for Chat ' + str(last_chat_id) + '.')
    custom_keyboard = [['/trivia', '/settings', '/help']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.sendMessage(update.message.chat_id, text='Hi and welcome to Shing\'s Trivia Bot!\n'
                    'You can start by trying one of the buttons below.', reply_markup=reply_markup)


def help(bot, update):
    custom_keyboard = [['/start', '/trivia', '/settings']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.sendMessage(update.message.chat_id, text='Command List\n'
                                             '/start - Welcome message\n'
                                             '/trivia - Starts a trivia session\n'
                                             '/stop - Stops a trivia session if in progress \n',
                                             reply_markup=reply_markup)


# Settings page
def settings(bot, update):
    last_chat_id = update.message.chat_id
    change[last_chat_id] = True
    changing[last_chat_id] = 0
    custom_keyboard = [['Time per Question', 'Questions per Round', 'EXIT']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.sendMessage(update.message.chat_id, text="What setting do you want to change?", reply_markup=reply_markup)


# Settings progress menu 1
def changesettings(bot, update):
    global change
    global changing
    last_chat_id = update.message.chat_id
    if change[last_chat_id] and update.message.text == 'Time per Question':
        custom_keyboard = [['5', '10', '15', '20', '25', '30', 'EXIT']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        bot.sendMessage(update.message.chat_id, text="How many seconds would you like to set per question?", reply_markup=reply_markup)
        changing[last_chat_id] = 1
    elif change[last_chat_id] and update.message.text == 'Questions per Round':
        custom_keyboard = [['5', '10', '15', '20', '25', '30', 'EXIT']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        bot.sendMessage(update.message.chat_id, text="How many questions would you like to set per round??", reply_markup=reply_markup)
        changing[last_chat_id] = 2
    elif change[last_chat_id] and update.message.text == 'EXIT':
        custom_keyboard = [['/trivia', '/settings', '/help']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        bot.sendMessage(update.message.chat_id, text="Exited settings.", reply_markup=reply_markup)
        change[last_chat_id] = False
        changing[last_chat_id] = 0
    elif change[last_chat_id] and changing[last_chat_id] == 0 and update.message.text != 'Questions per Round' and update.message.text != 'Time per Question':
        reply_markup = telegram.ReplyKeyboardHide()
        bot.sendMessage(update.message.chat_id, text="Error: Invalid choice.", reply_markup=reply_markup)
        change[last_chat_id] = False
        changing[last_chat_id] = 0


# Settings progress menu 2
def changeprogress(bot, update):
    global change
    global changing
    last_chat_id = update.message.chat_id
    if changing[last_chat_id] == 1 and update.message.text != 'Time per Question':
        trivia_timer = int(update.message.text)
        custom_keyboard = [['/trivia', '/help', '/settings']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        bot.sendMessage(update.message.chat_id, text="Setting successfully applied.", reply_markup=reply_markup)
        logger.info('[DEBUG]: Time per question set to ' + str(trivia_timer))
        change[last_chat_id] = False
        changing[last_chat_id] = 0
    elif changing[last_chat_id] == 2 and update.message.text != 'Questions per Round':
        session_length = int(update.message.text)
        custom_keyboard = [['/trivia', '/help', '/settings']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        bot.sendMessage(update.message.chat_id, text="Setting successfully applied.", reply_markup=reply_markup)
        logger.info('[DEBUG]: Questions per round set to ' + str(session_length))
        change[last_chat_id] = False
        changing[last_chat_id] = 0
    elif changing[last_chat_id] == 1 and update.message.text == 'EXIT' or changing[last_chat_id] == 2 and update.message.text == 'EXIT':
        reply_markup = telegram.ReplyKeyboardHide()
        bot.sendMessage(update.message.chat_id, text="Exited settings.", reply_markup=reply_markup)
        change[last_chat_id] = False
        changing[last_chat_id] = 0


# Start the trivia session.
def trivia(bot, update):
    global i
    global trivia_in_session
    last_chat_id = update.message.chat_id
    if trivia_in_session[last_chat_id]:
        bot.sendMessage(update.message.chat_id, text='Error! Trivia session already in progress!')
    else:
        trivia_in_session[last_chat_id] = True
        setup(bot, update)
        reply_markup = telegram.ReplyKeyboardHide()
        bot.sendMessage(update.message.chat_id, text='Trivia session starting. Get ready!\n'
                                                     'This round has %i questions.\n'
                                                     'Each question has a timer of %i seconds.\n'
                                                     'Note: You can stop the session at any time with /stop.' %
                                                     (session_length[last_chat_id], trivia_timer[last_chat_id]), reply_markup = reply_markup)
        setup(bot, update)
        i[last_chat_id] = session_length[last_chat_id]
        sendquestion(bot, update)


# Puts the "question" list into a dictionary called "bank".
def setup(bot, update):
    global bank
    last_chat_id = update.message.chat_id
    with open(qnfile[last_chat_id], 'r') as f:
        for line in f:
            (key, val) = line.split(' = ')
            bank[last_chat_id][key] = val
    bank[last_chat_id] = {k: i.strip() for k, i in bank[last_chat_id].items()}


# Prepares and prints a question from the "questions" list.
def sendquestion(bot, update):
    global qn
    global ans1
    global ans
    global trivia_await_answer
    global t1
    global t2
    last_chat_id = update.message.chat_id
    bot.sendMessage(update.message.chat_id, text='Preparing the next question...')
    n[last_chat_id] = randint(1, len(bank[last_chat_id])/2)
    qn[last_chat_id] = bank[last_chat_id]['Question' + str(n[last_chat_id])]
    ans1[last_chat_id] = (bank[last_chat_id]['Answer' + str(n[last_chat_id])]).split(', ')
    ans[last_chat_id] = [x.lower() for x in ans1[last_chat_id]]
    sleep(time_between_questions[last_chat_id])
    bot.sendMessage(update.message.chat_id, text='[TRIVIA] %s' % qn[last_chat_id])
    trivia_await_answer[last_chat_id] = True
    t1[last_chat_id] = Timer(trivia_timer[last_chat_id]/2, promptanswer, args=(bot, update, last_chat_id))
    t2[last_chat_id] = Timer(trivia_timer[last_chat_id], noanswer, args=(bot, update, last_chat_id))
    if trivia_await_answer[last_chat_id]:
        t1[last_chat_id].start()
        t2[last_chat_id].start()


def checkanswer(bot, update):
    global trivia_await_answer
    global trivia_in_session
    global i
    global t1
    global t2
    global score
    last_chat_id = update.message.chat_id
    attempt[last_chat_id] = update.message.text.lower()
    if trivia_await_answer[last_chat_id] and attempt[last_chat_id] in ans[last_chat_id]:
        trivia_await_answer[last_chat_id] = False
        bot.sendMessage(update.message.chat_id, text='%s is Correct!' % update.message.from_user.first_name)
        # Add score.
        if update.message.from_user.first_name in score[last_chat_id]:
            score[last_chat_id][update.message.from_user.first_name] += 1
        else:
            score[last_chat_id][update.message.from_user.first_name] = 1
        logger.info('[DEBUG] Current score sheet for Chat ' + str(last_chat_id) + ': ' + str(score[last_chat_id]))
        t1[last_chat_id].cancel()
        t2[last_chat_id].cancel()
        # Check loop.
        i[last_chat_id] -= 1
        logger.info('[DEBUG] Questions Left for Chat ' + str(last_chat_id) + ': ' + str(i[last_chat_id]))
        if i[last_chat_id] > 0:
            sendquestion(bot, update)
        elif i[last_chat_id] == 0:
            bot.sendMessage(update.message.chat_id, text='Trivia session ended. Thanks for playing!')
            topscorer[last_chat_id] = max(score.keys(), key=(lambda k: score[k]))
            bot.sendMessage(update.message.chat_id, text='The top scorer was %s with a score of %i.' %
                                                         (topscorer[last_chat_id], score[last_chat_id][topscorer]))
            i[last_chat_id] = session_length[last_chat_id]
            trivia_in_session[last_chat_id] = False
            score[last_chat_id] = {}


# Prompt for an answer with 5 seconds remaining.
def promptanswer(bot, update, last_chat_id):
    if trivia_await_answer[last_chat_id]:
        bot.sendMessage(update.message.chat_id, text='%i seconds remaining!' % (trivia_timer[last_chat_id]/2))


# Did not get an answer within the time period.
def noanswer(bot, update, last_chat_id):
    global trivia_await_answer
    global trivia_in_session
    global i
    global score
    if trivia_await_answer[last_chat_id]:
        trivia_await_answer[last_chat_id] = False
        bot.sendMessage(update.message.chat_id, text='Time\'s up! Unfortunately, no one got the answer :(\n'
                                                     'The correct answer was: %s' % ans1[last_chat_id][0])
        logger.info('[DEBUG] Current score sheet for Chat ' + str(last_chat_id) + ': ' + str(score[last_chat_id]))
        i[last_chat_id] -= 1
        logger.info('[DEBUG] Questions Left for Chat ' + str(last_chat_id) + ': ' + str(i[last_chat_id]))
        if i[last_chat_id] > 0:
            sendquestion(bot, update)
        elif i[last_chat_id] == 0:
            bot.sendMessage(update.message.chat_id, text='Trivia session ended. Thanks for playing!')
            topscorer = max(score.keys(), key=(lambda k: score[k]))
            bot.sendMessage(update.message.chat_id, text='The top scorer was %s with a score of %i.' %
                                                         (topscorer[last_chat_id], score[last_chat_id][topscorer]))
            i[last_chat_id] = session_length[last_chat_id]
            trivia_in_session[last_chat_id] = False
            score[last_chat_id] = {}


# Check if trivia is in session and if so, stops it.
def stop(bot, update):
    global trivia_in_session
    global trivia_await_answer
    last_chat_id = update.message.chat_id
    if trivia_in_session[last_chat_id]:
        trivia_in_session[last_chat_id] = False
        trivia_await_answer[last_chat_id] = False
        bot.sendMessage(update.message.chat_id, text='Trivia session stopped manually.')
        return
    else:
        bot.sendMessage(update.message.chat_id, text='ERROR: Trivia is not in session!')


def any_message(bot, update):
    """ Print to console """

    # Save last chat_id to use in reply handler
    global last_chat_id
    last_chat_id = update.message.chat_id

    logger.info("New message from: %s | chat_id: %d | Text: %s" %
                (update.message.from_user,
                 update.message.chat_id,
                 update.message.text))


def unknown_command(bot, update):
    """ Answer in Telegram """
    bot.sendMessage(update.message.chat_id, text='Command not recognized!')


# @run_async
# def message(bot, update, **kwargs):
    """
    Example for an asynchronous handler. It's not guaranteed that replies will
    be in order when using @run_async. Also, you have to include **kwargs in
    your parameter list. The kwargs contain all optional parameters that are
    """

#    sleep(2)  # IO-heavy operation here
#    bot.sendMessage(update.message.chat_id, text='Echo: %s' %
#                                                update.message.text)


# These handlers are for updates of type str. We use them to react to inputs
# on the command line interface
def cli_reply(bot, update, args):
    """
    For any update of type telegram.Update or str that contains a command, you
    can get the argument list by appending args to the function parameters.
    Here, we reply to the last active chat with the text after the command.
    """
    if last_chat_id is not 0:
        bot.sendMessage(chat_id=last_chat_id, text=' '.join(args))


def cli_noncommand(bot, update, update_queue):
    """
    You can also get the update queue as an argument in any handler by
    appending it to the argument list. Be careful with this though.
    Here, we put the input string back into the queue, but as a command.
    To learn more about those optional handler parameters, read:
    http://python-telegram-bot.readthedocs.org/en/latest/telegram.dispatcher.html
    """
    update_queue.put('/%s' % update)


def unknown_cli_command(bot, update):
    logger.warn("Command not found: %s" % update)


def error(bot, update, error):
    """ Print error to console """
    logger.warn('Update %s caused error %s' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    token = '203435568:AAFtnHEPa2H1ZKLz0nX50A1K50I47sbndiA'
    updater = telegram.Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # This is how we add handlers for Telegram messages
    dp.addTelegramCommandHandler("start", start)
    dp.addTelegramCommandHandler("help", help)
    dp.addTelegramCommandHandler("trivia", trivia)
    dp.addTelegramCommandHandler("stop", stop)
    dp.addTelegramCommandHandler("settings", settings)
    dp.addUnknownTelegramCommandHandler(unknown_command)
    # Message handlers only receive updates that don't contain commands
    dp.addTelegramMessageHandler(checkanswer)
    dp.addTelegramMessageHandler(changesettings)
    dp.addTelegramMessageHandler(changeprogress)
    # Regex handlers will receive all updates on which their regex matches
    dp.addTelegramRegexHandler('.*', any_message)

    # String handlers work pretty much the same
    dp.addStringCommandHandler('reply', cli_reply)
    dp.addUnknownStringCommandHandler(unknown_cli_command)
    dp.addStringRegexHandler('[^/].*', cli_noncommand)

    # All TelegramErrors are caught for you and delivered to the error
    # handler(s). Other types of Errors are not caught.
    dp.addErrorHandler(error)

    # Start the Bot and store the update Queue, so we can insert updates
    update_queue = updater.start_polling(poll_interval=0.1, timeout=10)

    '''
    # Alternatively, run with webhook:
    updater.bot.setWebhook(webhook_url='https://example.com/%s' % token,
                           certificate=open('cert.pem', 'rb'))
    update_queue = updater.start_webhook('0.0.0.0',
                                         443,
                                         url_path=token,
                                         cert='cert.pem',
                                         key='key.key')
    # Or, if SSL is handled by a reverse proxy, the webhook URL is already set
    # and the reverse proxy is configured to deliver directly to port 6000:
    update_queue = updater.start_webhook('0.0.0.0',
                                         6000)
    '''

    # Start CLI-Loop
    while True:
        text = input()

        # Gracefully stop the event handler
        if text == 'stop':
            updater.stop()
            break

        # else, put the text into the update queue to be handled by our handlers
        elif len(text) > 0:
            update_queue.put(text)

if __name__ == '__main__':
    main()
