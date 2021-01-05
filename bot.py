#!/usr/bin/env python3

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup
import logging
import sys
import random
import math

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
captain_id = ""
votes = []
voted = []
living_player_id_list = []
player_names = []
choices = ["up", "down", "right", "left", "stay"]
choice = ""
course = 50
spacesuit_maintainer = ""
oxygen_maintainer = ""
to_die = ""

height = 3
length = 5
asteroid_chance = 4 # 1 in 4
heading_position = [random.randint(1,height), random.randint(1,length)]
target_position = [random.randint(1,height), random.randint(1,length)]
asteroid_positions = []


dead_players = []
distance_from_home = 50
oxygen = 100
day = 0


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
    global captain_id
    send_to_all(context, "Captain " + captain + " will now steer the ship")
    captain_id = living_player_id_list[get_item_index(player_names, captain)]
    steering_minigame(context, False)


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


def distance(start, end):
    # get distance using pythagorean theroum
    a = abs(start[0] - end[0])
    b = abs(start[1] - end[1])
    c = math.sqrt(math.pow(a, 2) + math.pow(b, 2))
    return c


def validate_steering_position(new_position, height, length, asteroid_positions):
    if new_position[0] > 0 and new_position[0] <= height:
        if new_position[1] > 0 and new_position[1] <= length:
            if new_position not in asteroid_positions:
                return 0
            else:
                return 1
        else:
            return 2
    else:
        return 2


def steering_minigame(context, testing):
    global state
    global course
    global choice
    global choices
    global height
    global length
    global asteroid_chance
    global heading_position
    global target_position
    global asteroid_positions

    if testing:
        def send_cap(context, message):
            print(message)
        state = 6
    else:
        def send_cap(context, message):
            context.bot.send_message(captain_id, message)

    if state == 6:
        send_cap(context, "You will need to steer your ship '+' towards your target 'o' and avoid asteroids '*'")
        send_cap(context, "Unless you're the imposter, then steer the the ship off course. But not too much or the crewmates will catch on")
        send_cap(context, "If you can't see the target, the ship is already on top of it")
        send_cap(context, "Here is the map:")

        asteroid_positions = generate_asteroids(height, length, asteroid_chance)
        map = redraw(height, length, heading_position, target_position, asteroid_positions)
        send_cap(context, map)
        send_cap(context, "Send 'up', 'down', 'left', 'right', or 'stay' to steer the ship")
        if testing:
            choice = input()
            state =  8
        else:
            state = 7
    if state == 8:
        new_position = heading_position[:]
        if choice == "up":
            new_position[0] -= 1
        elif choice == "down":
            new_position[0] += 1
        elif choice == "right":
            new_position[1] += 1
        elif choice == "left":
            new_position[1] -= 1

        validation = validate_steering_position(new_position, height, length, asteroid_positions)
        if validation == 2:
            send_cap(context, "Error: you cannot move off screen")
            new_position = heading_position[:]
        elif validation == 1:
            send_cap(context, "Error: you hit an asteroid")
            new_position = heading_position[:]
        else:
            heading_position = new_position[:]
        send_cap(context, redraw(height, length, heading_position, target_position, asteroid_positions))
        course += distance(heading_position, target_position)
        if course > 100:
            course = 100
            if course < 0:
                course = 0
        send_to_all(context, "The ship has been steered")
        state = 9
        assign_jobs(context)


def assign_jobs(context):
    global spacesuit_maintainer
    global oxygen_maintainer
    global state

    if state == 9:
        spacesuit_maintainer = ""
        oxygen_maintainer = ""
        while spacesuit_maintainer == "":
            new = random.choice(living_player_id_list)
            if choice != captain_id:
                spacesuit_maintainer = new
        while oxygen_maintainer == "":
            new = random.choice(living_player_id_list)
            if choice != captain and choice != spacesuit_maintainer:
                oxygen_maintainer = new
        state = 10
        maintain_spacesuits(context)


def maintain_spacesuits(context):
    global to_die
    global state

    if state == 10:
        context.bot.send_message(spacesuit_maintainer,"You are the spacesuit maintainer, you may choose to maintain or sabotage the spacesuits. Type 'maintain' or 'sabotage'")
        state = 11

def non_command(update, context):
    global state
    global imposter_amount
    global votes
    global voted
    global choice
    global to_die

    print("received message " + update.message.text)

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

    elif state == 4: # getting votes
        if update.message.chat_id in living_player_id_list:
            if update.message.chat_id not in voted:
                voted.append(update.message.chat_id)
                if update.message.text in player_names:
                    votes.append(update.message.text)
        if len(voted) == len(living_players):
            state = 5
            vote(context)
            return
    elif state == 7:
        if update.message.chat_id == captain_id:
            if update.message.text.lower() in choices:
                choice = update.message.text.lower()
                state = 8
                steering_minigame(context, False)
                return
    elif state == 11:
        if update.message.chat_id == spacesuit_maintainer:
            if update.message.text.lower() == "maintain":
                context.bot.send_message(spacesuit_maintainer,"You have chosen to maintain the spacesuits")
                state = 12
                # TODO next function here
                return
            elif update.message.text.lower() == "sabotage":
                context.bot.send_message(spacesuit_maintainer,"Enter the player whose suit you want to sabotage")
                context.bot.send_message(spacesuit_maintainer, player_names)
                state = 13
                return
    elif state == 13:
        if update.message.chat_id == spacesuit_maintainer:
            if update.message.text in player_names:
                to_die = update.message.text
                print(to_die)
                state = 12
                # TODO next function here
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
