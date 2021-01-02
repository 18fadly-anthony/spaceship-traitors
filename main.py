#!/usr/bin/env python3

# Among Us Spin Off game proof of concept

import sys


def get_int(prompt):
    while True:
        value = input(prompt)
        try:
            value = int(value)
            return value
        except ValueError:
            print("Please enter a number")


players = []
imposters = []


def setup_game():
    global players
    global imposters

    player_amount = get_int("Enter amount of players: ")

    for i in range(player_amount):
        players += str(input("Enter player name: "))

    imposter_amount = 0
    while imposter_amount < 1 or imposter_amount >= (player_amount / 2):
        imposter_amount = get_int("Enter amount of imposters, it must be less than half of players: ")


def main():
    setup_game()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\n' + "exit")
        sys.exit(0)