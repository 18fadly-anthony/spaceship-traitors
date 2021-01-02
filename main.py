#!/usr/bin/env python3

import sys

def get_int(prompt):
    while True:
        value = input(prompt)
        value = int(value)

players = []
imposters = []

def setup_game():
    print("placeholder")

def main():
    get_int("test")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\n' + "exit")
        sys.exit(0)
