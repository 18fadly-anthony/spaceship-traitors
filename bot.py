#!/usr/bin/env python3

# Copyright (c) 2021 Anthony Fadly (18fadly.anthony@gmail.com)
# This program is licensed under the GNU Affero General Public License
# You are free to copy, modify, and redistribute the code.
# See LICENSE file and COPYING file.

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup
import logging
import sys
import random
import math
import time

random.seed(time.time())

game_state = "not running"
host = ""
imposter_amount = 0
state = 0
captain = ""
captain_id = ""
votes = []
voted = []
choices = ["up", "down", "right", "left", "stay"]
choice = ""
course = 50
spacesuit_maintainer = ""
oxygen_maintainer = ""
to_die = ""
oxygen = 75
distance_from_home = 50
day = 0
max_imposters = 0

height = 5
length = 10
asteroid_chance = 4 # 1 in 4
heading_position = [random.randint(1,height), random.randint(1,length)]
target_position = [random.randint(1,height), random.randint(1,length)]
asteroid_positions = []

player_names = []
player_ids = []
living_player_names = []
living_player_ids = []
dead_player_names = []

imposter_names = []
imposter_ids = []
living_imposter_names = []


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


def source(update, context):
    if len(sys.argv) > 2:
        message = str(sys.argv[2])
    else:
        message = "Whoever is hosting the bot did not provide a link to the source code and is in violation of the AGPL, please complain about this to them"
    update.message.reply_text(message)


def startgame(update, context):
    global game_state
    global host
    global player_names
    global player_ids
    if game_state == "not running":
        player_ids = []
        player_names = []
        game_state = "lobby"
        host = update.message.from_user.first_name
        print(host + " is starting a game")
        player_names.append(host)
        player_ids.append(update.message.chat_id)
        update.message.reply_text('Starting a game... you are the host, ' + host)
        update.message.reply_text('Waiting for players...')
    else:
        update.message.reply_text('Error: a game has already started')


def joingame(update, context):
    global player_names
    global player_ids
    if game_state == "lobby":
        new_player_name = update.message.from_user.first_name
        new_player_id = update.message.chat_id
        if new_player_name in player_names:
            context.bot.send_message(new_player_id, "Error you, or someone with your first name on telegram, is already in the game")
            return
        elif new_player_name == host:
            context.bot.send_message(new_player_id, "Error you, or someone with your first name on telegram, is already in the game")
            return
        player_names.append(new_player_name)
        player_ids.append(new_player_id)
        update.message.reply_text('You have joined ' + host + "'s game")
        context.bot.send_message(player_ids[0], new_player_name + " has joined your game")
        print(new_player_name + " has joined " + player_names[0] + "'s game")
        if len(player_names) > 2:
            context.bot.send_message(player_ids[0], "There are " + str(len(player_names)) + " players in your lobby, send /begin to start the game")


def send_to_all(context, message):
    for i in living_player_ids:
        context.bot.send_message(i, message)


def send_to_all_inc(context, message):
    for i in player_ids:
        context.bot.send_message(i, message)


def reply_keyboard_to_all(context, message, menu_markup):
    for i in living_player_ids:
        context.bot.send_message(chat_id=i, text=message, reply_markup=menu_markup)


def decide_maintain(player_id, context, message):
    menu_keyboard = [['maintain'], ['sabotage']]
    menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=player_id, text=message, reply_markup=menu_markup)


def setup_game(context):
    global state
    global living_player_names
    global living_player_ids
    global imposter_ids
    global imposter_names
    global living_imposter_names
    global max_imposters
    if state == 0:
        living_player_names = player_names[:]
        living_player_ids = player_ids[:]
        max_imposters = math.ceil(len(living_player_ids) / 2)
        menu_keyboard = []
        for i in range(1, max_imposters):
            menu_keyboard.append([str(i)])
        menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
        context.bot.send_message(chat_id=player_ids[0], text="Set amount of imposters, it must be less than " + str(max_imposters), reply_markup=menu_markup)
        state = 1 # to set amount of imposters
    elif state == 2: # set imposters
        while not len(imposter_ids) == imposter_amount:
            new_imposter_id = random.choice(player_ids)
            if not new_imposter_id in imposter_ids:
                imposter_ids.append(new_imposter_id)
                imposter_names.append(player_names[get_item_index(player_ids, new_imposter_id)])
        living_imposter_names = imposter_names[:]

        # inform the imposters
        for i in imposter_ids:
            context.bot.send_message(i, "You are an imposter")

        state = 3
        vote(context)


def begin(update, context):
    global game_state
    game_state = "running"
    if not len(player_ids) > 2:
        context.bot.send_message(player_ids[0], "Error: not enough players have joined")
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

        randomized_players = living_player_names[:]
        random.shuffle(randomized_players)

        menu_keyboard = []
        for i in randomized_players:
            menu_keyboard.append([i])
        menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)

        reply_keyboard_to_all(context, "Vote for a captain who will steer the ship, enter one of the following:", menu_markup)

        state = 4
    if state == 5:
        captain = max(votes, key = votes.count)
        state = 6
        steer(context)


def steer(context):
    global course
    global captain_id
    send_to_all(context, "The captain is steering the ship")
    captain_id = player_ids[get_item_index(player_names, captain)]
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
                map += ("x")
            else:
                map += ("~")
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
        msg = "You will need to steer your ship '+' towards your target 'o' and avoid asteroids 'x' \n \n Unless you're the imposter, then steer the the ship off course. But not too much or the crewmates will catch on \n If you can't see the target, the ship is already on top of it"
        send_cap(context, msg)
        send_cap(context, "Here is the map:")

        asteroid_positions = generate_asteroids(height, length, asteroid_chance)
        map = redraw(height, length, heading_position, target_position, asteroid_positions)
        send_cap(context, map)

        menu_keyboard = [['up'], ['down'], ['left'], ['right'], ['stay']]
        menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
        context.bot.send_message(chat_id=captain_id, text="Steer the ship " + str(max_imposters), reply_markup=menu_markup)

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
        if testing:
            print(distance(heading_position, target_position))
        course -= (distance(heading_position, target_position) - 5)
        if course > 100:
            course = 100
        elif course < 0:
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
            new = random.choice(living_player_ids)
            if new != captain_id:
                spacesuit_maintainer = new
        while oxygen_maintainer == "":
            new = random.choice(living_player_ids)
            if new != captain_id and new != spacesuit_maintainer:
                oxygen_maintainer = new
        state = 10
        maintain_spacesuits(context)


def maintain_spacesuits(context):
    global to_die
    global state

    if state == 10:
        send_to_all(context, "The spacesuit maintainer is maintaining spacesuits")
        decide_maintain(spacesuit_maintainer, context, "You are the spacesuit maintainer, you may choose to maintain the spacesuits or sabotage a specific spacesuit causing that player to die.")
        state = 11


def maintain_oxygen(context):
    global state

    if state == 13:
        send_to_all(context, "The oxygen maintainer is maintaining oxygen")
        decide_maintain(oxygen_maintainer, context, "You are the oxygen maintainer, you man choose to maintain the oxygen or sabotage it by leaking it.")
        state = 14


def spacewalk(context):
    global state
    global to_die
    global living_player_names
    global living_player_ids
    global dead_player_names
    global living_imposter_names

    if state == 15:
        send_to_all(context, "It's time for a spacewalk, everyone will wear a spacesuit and venture outside the ship, except for the captain who will maintain the ship")
        if to_die == captain:
            to_die = ""
            context.bot.send_message(captain_id, "An attempt has been made on your life!")
        elif to_die in living_player_names:
            del living_player_ids[get_item_index(living_player_names, to_die)]
            del living_player_names[get_item_index(living_player_names, to_die)]
            dead_player_names.append(to_die)
            if to_die in living_imposter_names:
                del living_imposter_names[get_item_index(living_imposter_names, to_die)]
            send_to_all_inc(context, to_die + "'s spacesuit failed!")
            send_to_all_inc(context, to_die + " has died!")
            to_die = ""
        state = 16
        travel(context)


def travel(context):
    global state
    global distance_from_home
    global oxygen
    global day

    if state == 16:
        distance_from_home -= (course / 10)
        oxygen -= random.randint(1,10)
        day += 1
        state = 17
        status(context)


def status(context):
    global state

    if state == 17:
        status_msg = ""

        status_msg += "--- STATUS REPORT --- \n\n"
        status_msg += ("It is day " + str(day) + " \n")
        status_msg += ("There are " + str(len(living_player_ids)) + " astronauts on deck \n")
        status_msg += (str(len(dead_player_names)) + " astronauts have died \n")
        status_msg +=("There are " + str(len(living_imposter_names)) + " imposters on deck \n")
        status_msg += ("We are " + str(distance_from_home) + " lightyears away from home \n")
        status_msg += ("We have " + str(oxygen) + " units of oxygen remaining \n")
        status_msg += ("We are " + str(course) + " percent on course")

        send_to_all_inc(context, status_msg)

        if distance_from_home < 1:
            send_to_all_inc(context, "You made it home!")
            state = 18
            win(context)
        elif len(living_imposter_names) < 1:
            send_to_all_inc(context, "All imposters have been killed!")
            state = 18
            win(context)
        elif oxygen < 1:
            send_to_all_inc(context, "You are out of oxygen!")
            state = 19
            lose(context)
        elif len(living_imposter_names) >= (len(living_player_ids) / 2):
            send_to_all_inc(context, "Imposters outnumber crewmates!")
            state = 19
            lose(context)
        else:
            state = 3
            vote(context)


def win(context):
    global state
    global game_state

    if state == 18:
        send_to_all_inc(context, "Crewmates Win! \n The imposter(s) were: \n" + str(imposter_names))
        state = 0
        game_state = "not running"


def lose(context):
    global state
    global game_state
    if state == 19:
        send_to_all_inc(context, "Game Over! The imposter(s) won! The imposter(s) were: \n" + str(imposter_names))
        state = 0
        game_state = "not running"


def non_command(update, context):
    global state
    global imposter_amount
    global votes
    global voted
    global choice
    global to_die
    global oxygen

    print("received message " + update.message.text + " from " + update.message.from_user.first_name)

    if state == 1: # set amount of imposters
        while imposter_amount < 1 or imposter_amount >= (len(player_ids) / 2):
            if update.message.chat_id == player_ids[0]:
                try:
                    imposter_amount = int(update.message.text)
                except ValueError:
                    pass
        state = 2
        setup_game(context)
        return

    elif state == 4: # getting votes
        if update.message.chat_id in living_player_ids:
            if update.message.chat_id not in voted:
                voted.append(update.message.chat_id)
                if update.message.text in living_player_names:
                    votes.append(update.message.text)
        if len(voted) == len(living_player_ids):
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
                state = 13
                maintain_oxygen(context)
                return
            elif update.message.text.lower() == "sabotage":
                menu_keyboard = []
                for i in living_player_names:
                    menu_keyboard.append([i])
                menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
                context.bot.send_message(chat_id=spacesuit_maintainer, text = "Enter the player whose suit you want to sabotage", reply_markup = menu_markup)
                state = 12
                return
    elif state == 12:
        if update.message.chat_id == spacesuit_maintainer:
            if update.message.text in living_player_names:
                to_die = update.message.text
                state = 13
                maintain_oxygen(context)
                return
    elif state == 14:
        if update.message.chat_id == oxygen_maintainer:
            if update.message.text.lower() == "maintain":
                context.bot.send_message(oxygen_maintainer, "You have chosen to maintain the oxygen")
                oxygen += 5
            elif update.message.text.lower() == "sabotage":
                context.bot.send_message(oxygen_maintainer, "You have chosen to sabotage the oxygen")
                oxygen -= 10
            state = 15
            spacewalk(context)


def main():
    updater = Updater(sys.argv[1], use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("startgame", startgame))
    dp.add_handler(CommandHandler("joingame", joingame))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("begin", begin))
    dp.add_handler(CommandHandler("source", source))
    dp.add_handler(MessageHandler(Filters.text, non_command))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
