#!/usr/bin/env python3

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup
import logging
import sys
import random

#API_KEY = str(sys.argv[1])

game_state = "not running"
players = []
host = ""
living_players = []
imposter_amount = 0
state = 0
imposters = []
living_imposters = []
captain = ""
votes = []
voted = []
living_player_id_list = []
player_names = []

dead_players = []
course = 50
distance_from_home = 50
oxygen = 100
day = 0
spacesuit_maintainer = ""
oxygen_maintainer = ""
to_die = ""


def get_item_index(array, item):
    for i in range(len(array)):
        if array[i] == item:
            return i


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    if game_state == "not running":
        update.message.reply_text('A game is not running, send /startgame to start one')
    elif game_state == "running":
        update.message.reply_text('The game has already started, please wait until it is over')
    elif game_state == "lobby":
        update.message.reply_text('A lobby is open, send /joingame to join it')


def help(update, context):
    """Send a message when the command /help is issued."""
    if game_state == "not running":
        update.message.reply_text('A game is not running, send /startgame to start one')
    elif game_state == "running":
        update.message.reply_text('The game has already started, please wait until it is over')
    elif game_state == "lobby":
        update.message.reply_text('A lobby is open, send /joingame to join it')


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def startgame(update, context):
    global game_state
    global players
    global host
    if game_state == "not running":
        game_state = "lobby"
        host = update.message.from_user.first_name
        print(host + " is starting a game")
        players.append([host, update.message.chat_id])
        update.message.reply_text('Starting a game... you are the host, ' + host)
        update.message.reply_text('Waiting for players...')
    else:
        update.message.reply_text('Error: a game has already started')


def joingame(update, context):
    if game_state == "lobby":
        new_player = [update.message.from_user.first_name, update.message.chat_id]
        players.append(new_player)
        update.message.reply_text('You have joined ' + host + "'s game")
        context.bot.send_message(players[0][1], new_player[0] + " has joined your game")
        print(new_player[0] + " has joined " + players[0][0] + "'s game")
        if len(players) > 2:
            context.bot.send_message(players[0][1], "There are " + str(len(players)) + " players in your lobby, send /begin to start the game")


def send_to_all(context, message):
    for i in players:
        context.bot.send_message(i[1], message)

def update_player_ids():
    global living_player_id_list
    global player_names
    living_player_id_list = []
    player_names = []
    for i in range(len(living_players)):
        living_player_id_list.append(living_players[i][1])
        player_names.append(living_players[i][0])


def setup_game(context):
    global state
    global living_players
    if state == 0:
        living_players = players[:]
        update_player_ids()
        context.bot.send_message(players[0][1], "Set amount of imposters")
        state = 1 # to set amount of imposters
    elif state == 2: # set imposters
        while not len(imposters) == imposter_amount:
            new_imposter = random.choice(players)
            if not new_imposter in imposters:
                imposters.append(new_imposter)
        living_imposters = imposters[:]

        # inform the imposters
        for i in imposters:
            context.bot.send_message(i[1], i[0] + " you are an imposter")

        state = 3
        #print("would run vote() here") # TODO remove this
        vote(context)


def begin(update, context):
    #if not len(players) > 2: # TODO You need 3 or more players for an actual game but I'm setting it to 1 or more for testing
    if not len(players) > 1:
        context.bot.send_message(players[0][1], "Error: not enough players have joined")
        return
    send_to_all(context, "Starting the Game!")
    setup_game(context)


def vote(context):
    global captain
    global state
    global votes
    global voted

    if state == 3:
        votes = []
        voted = []

        send_to_all(context, "Vote for a captain who will steer the ship, enter one of the following:")
        send_to_all(context, str(player_names))

        state = 4
    if state == 5:
        captain = max(votes, key = votes.count)
        send_to_all(context, "The captain is " + captain)
        state = 6
        steer(context)


def steer(context):
    global course
    send_to_all(context, "Captain " + captain + " will now steer the ship")
    captain_id = living_player_id_list[get_item_index(player_names, captain)]
    course += (10 - steering_minigame(context, captain_id, False))
    if course > 100:
        course = 100
    if course < 0:
        course = 0


def redraw(height, length, position, target_position, asteroid_positions):
    map = ""
    for i in range(1, height + 1):
        for j in range(1, length + 1):
            if [i, j] == position:
                map += ("+")
            elif [i, j] == target_position:
                map += ("o")
            elif [i, j] in asteroid_positions:
                map += ("*")
            else:
                map += (".")
        map += "\n"
    return map


def generate_asteroids(height, length, chance):
    asteroid_positions = []
    for i in range(1, height + 1):
        for j in range(1, length + 1):
            if random.randint(1,chance) == 1:
                asteroid_positions.append([i, j])
    return asteroid_positions


def steering_minigame(context, captain_id, testing):
    if testing:
        def send_cap(context, captain_id, message):
            print(message)
    else:
        def send_cap(context, captain_id, message):
            context.bot.send_message(captain_id, message)

    send_cap(context, captain_id, "You will need to steer your ship '+' towards your target 'o' and avoid asteroids '*'")
    send_cap(context, captain_id, "Unless you're the imposter, then steer the the ship off course. But not too much or the crewmates will catch on")
    send_cap(context, captain_id, "Here is the map:")

    height = 5
    length = 10
    asteroid_chance = 4 # 1 in 4
    heading_position = [random.randint(1,height), random.randint(1,length)]
    target_position = [random.randint(1,height), random.randint(1,length)]
    asteroid_positions = generate_asteroids(height, length, asteroid_chance)
    map = redraw(height, length, heading_position, target_position, asteroid_positions)
    if testing:
        print(map)
    else:
        send_cap(context, captain_id, map)
    choice_amount = random.randint(1, 5)


def non_command(update, context):
    global state
    global imposter_amount
    global votes
    global voted

    if state == 1: # set amount of imposters
        while imposter_amount < 1: # or imposter_amount >= (len(players) / 2): # TODO, uncomment this when no longer testing
            if update.message.chat_id == players[0][1]:
                try:
                    imposter_amount = int(update.message.text)
                except ValueError:
                    pass
        state = 2
        setup_game(context)
        return

    if state == 4: # getting votes
        if update.message.chat_id in living_player_id_list:
            if update.message.chat_id not in voted:
                voted.append(update.message.chat_id)
                if update.message.text in player_names:
                    votes.append(update.message.text)
        if len(voted) == len(living_players):
            state = 5
            vote(context)
            return


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(sys.argv[1], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("startgame", startgame))
    dp.add_handler(CommandHandler("joingame", joingame))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("begin", begin))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(MessageHandler(Filters.text, non_command))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
