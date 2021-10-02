def chooseLife(print, sack):
    while True:
        print("Choose one of the following")
        lifeChoice = "Life"
        deathChoice = "Death"
        choice = yield [lifeChoice, deathChoice,]
        if choice == deathChoice:
            print("I don't think you wanted to do that")
            continue
        else:
            print("Well done, you made the right choice")
            break

