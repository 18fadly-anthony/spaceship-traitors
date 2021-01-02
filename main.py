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


def vote():
    global players
    global imposters

    print()
    print("vote for a captain who will steer the ship")
    print("if there is a tie, the GAME will decide on the captain")
    print("the candidates are:")
    print(players)
    print("any votes that aren't from the list of candidates will be spoiled")


    votes = []
    for i in players:
        choice = get_string(i + ", enter your vote: ")
        if choice in players:
            votes += choice
        else:
            print("that was not a candidate, your vote was not counted")
        
    return(max(votes,key=votes.count))


def main():
    global players
    global imposters
    setup_game()
    captain = vote()
    print("your captain is " + captain + ", they will steer the ship")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\n' + "exit")
        sys.exit(0)
