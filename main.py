#!/usr/bin/env python3

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
    player_amount = get_int("Enter amount of players: ")

def main():
    setup_game()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\n' + "exit")
        sys.exit(0)
