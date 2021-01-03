#!/usr/bin/env python3

# Among Us Spin Off game proof of concept text adventure

import sys
import random
import math


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
course = 50
distance_from_home = 50
oxygen = 100
day = 0
spacesuit_maintainer = ""
oxygen_maintainer = ""
captain = ""


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
            players.append(player)

    imposter_amount = 0
    while imposter_amount < 1 or imposter_amount >= (player_amount / 2):
        imposter_amount = get_int("Enter amount of imposters, it must be less than half of players: ")

    while not len(imposters) == imposter_amount:
        imposter = random.choice(players)
        if not imposter in imposters:
            imposters.append(imposter)

    for i in imposters:
        print(i + ", you are an imposter")


def vote():
    global players
    global captain

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
            votes.append(choice)
        else:
            print("that was not a candidate, your vote was not counted")

    captain = max(votes,key=votes.count)


def status():
    global players
    global imposters
    global course
    global distance_from_home
    global oxygen
    global day

    print()
    print("--- Status Report ---")
    print()
    print("It is day " + str(day))
    print("There are " + str(len(players)) + " astronauts on deck")
    print("There are " + str(len(imposters)) + " imposters on deck")
    print("We are " + str(distance_from_home) + " lightyears away from home")
    print("We have " + str(oxygen) + " units of oxygen remaining")
    print("We are " + str(course) + " percent on course")


def steer():
    global captain
    print()
    print(captain + " it is time to steer the ship")
    global course
    course += (10 - steering_minigame())
    if course > 100:
        course = 100
    if course < 0:
        course = 0


def redraw(height, length, position, target_position, asteroid_positions):
    for i in range(length):
        sys.stdout.write("_")
    print()
    for i in range(1, height + 1):
        for j in range(1, length + 1):
            if [i, j] == position:
                sys.stdout.write("+")
            elif [i, j] == target_position:
                sys.stdout.write("o")
            elif [i, j] in asteroid_positions:
                sys.stdout.write("*")
            else:
                sys.stdout.write(".")
        print()
    for i in range(length):
        sys.stdout.write("_")
    print()


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


def distance(start, end):
    # get distance using pythagorean theroum
    a = abs(start[0] - end[0])
    b = abs(start[1] - end[1])
    c = math.sqrt(math.pow(a, 2) + math.pow(b, 2))
    return c


def steering_minigame():
    print("Welcome to steering")
    print("You will need to steer your ship '+' towards your target 'o' and avoid asteroids '*'")
    print("Unless you're the imposter, then steer the the ship off course")
    print("but not too much or the crewmates will catch on")
    print("Here is the map:")
    height = 5
    length = 10
    heading_position = [random.randint(1,height), random.randint(1,length)]
    target_position = [random.randint(1,height), random.randint(1,length)]
    asteroid_positions = []
    for i in range(length):
        sys.stdout.write("_")
    print()
    for i in range(1, height + 1):
        for j in range(1, length + 1):
            if [i, j] == heading_position:
                sys.stdout.write("+")
            elif [i, j] == target_position:
                sys.stdout.write("o")
            else:
                if random.randint(1,4) > 1:
                    sys.stdout.write(".")
                else:
                    sys.stdout.write("*")
                    asteroid_positions.append([i, j])
        print()
    for i in range(length):
        sys.stdout.write("_")
    print()
    choice_amount = random.randint(1,5)
    choices = ["up", "down", "right", "left", "stay"]
    new_position = heading_position[:]
    while choice_amount > 0:
        print("You have " + str(choice_amount) + " moves remaining")
        choice = get_string("Type up, down, right, left, or stay to steer the ship: ")
        choice = choice.lower()
        if choice in choices:
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
                print("Error: you cannot move off screen")
                new_position = heading_position[:]
            elif validation == 1:
                print("Error: you hit an asteroid")
                new_position = heading_position[:]
            else:
                heading_position = new_position[:]
                choice_amount -= 1
            redraw(height, length, new_position, target_position, asteroid_positions)
    return(distance(heading_position, target_position))


def assign_jobs():
    global player
    global spacesuit_maintainer
    global oxygen_maintainer
    global captain
    spacesuit_maintainer = ""
    oxygen_maintainer = ""
    while spacesuit_maintainer == "":
        choice = random.choice(players)
        if choice != captain:
            spacesuit_maintainer = choice
    while oxygen_maintainer == "":
        choice = random.choice(players)
        if choice != captain and choice != spacesuit_maintainer:
            oxygen_maintainer = choice


def travel():
    global distance_from_home
    global course
    global oxygen
    global day
    distance_from_home -= (course / 10)
    oxygen -= 10
    day += 1

def main():
    setup_game()
    while distance_from_home > 0:
        vote()
        steer()
        assign_jobs()
        travel()
        status()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\n' + "Exiting...")
        sys.exit(0)
