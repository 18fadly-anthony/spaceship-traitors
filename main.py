#!/usr/bin/env python3

# Among Us Spin Off game proof of concept text adventure

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
course = 100


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
            votes.append(choice)
        else:
            print("that was not a candidate, your vote was not counted")

    return(max(votes,key=votes.count))


def status():
    global course
    print("the ship is " + str(course) + " percent on course")


def steer(captain):
    print()
    global course
    steered = False
    while not steered:
        choice = get_string(captain + ", it is time to steer the ship, in the future there will be a minigame for this but for now just type 'steer' or 'sabotage': ")
        if choice == "steer":
            course += 10
            if course > 100:
                course = 100
            steered = True
        elif choice == "sabotage":
            course -= 10
            if course < 0:
                course = 0
            steered = True
        else:
            print("Please enter 'steered' or 'sabotage'")


def redraw(height, length, heading_position, target_position, asteriod_positions):
    for i in range(length):
        sys.stdout.write("_")
    print()
    for i in range(1, height + 1):
        for j in range(1, length + 1):
            if [i, j] == heading_position:
                sys.stdout.write("+")
            elif [i, j] == target_position:
                sys.stdout.write("o")
            elif [i, j] in asteriod_positions:
                sys.stdout.write("*")
            else:
                sys.stdout.write(".")
        print()
    for i in range(length):
        sys.stdout.write("_")
    print()


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
    asteriod_positions = []
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
                    asteriod_positions.append([i, j])
        print()
    for i in range(length):
        sys.stdout.write("_")
    print()
    #redraw(height, length, heading_position, target_position, asteriod_positions)
    choice_made = False
    choices = ["up", "down", "right", "left", "stay"]
    while not choice_made:
        choice = get_string("Type up, down, right, left, or stay to steer the ship: ")
        choice = choice.lower()
        if choice in choices:
            new_position = heading_position
            if choice == "up":
                new_position[0] -= 1
            elif choice == "down":
                new_position[0] += 1
            elif choice == "right":
                new_position[1] += 1
            elif choice == "left":
                new_position[1] -= 1
            redraw(height, length, new_position, target_position, asteriod_positions)



def main():
    global players
    global imposters
    #setup_game()
    #captain = vote()
    #print("your captain is " + captain + ", they will steer the ship")
    #steer(captain)
    #status()
    steering_minigame()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\n' + "exit")
        sys.exit(0)
