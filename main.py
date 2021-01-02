#!/usr/bin/env python3

# Among Us Spin Off game proof of concept

import sys
import random


def get_int(prompt):
    while True:
        value = input(prompt)
        try:
            value = int(value)
            return value
        except ValueError:
            print("Please enter a number")


def get_string(prompt):
    while True:
        value = input(prompt)
        if value != "":
            return str(value)


players = []
imposters = []


def setup_game():
    global players
    global imposters

    player_amount = get_int("Enter amount of players: ")
    while player_amount < 3:
        print("You need at least 3 players")
        player_amount = get_int("Enter amount of players: ")

    while not len(players) == player_amount:
        player = get_string("Enter player name: ")
        if player in players:
            print ("That name is taken")
        else:
            players += player

    imposter_amount = 0
    while imposter_amount < 1 or imposter_amount >= (player_amount / 2):
        imposter_amount = get_int("Enter amount of imposters, it must be less than half of players: ")

    while not len(imposters) == imposter_amount:
        imposter = random.choice(players)
        if not imposter in imposters:
            imposters += imposter


def main():
    global players
    global imposters
    setup_game()
    print("players:")
    print(players)
    print("imposters:")
    print(imposters)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\n' + "exit")
        sys.exit(0)
