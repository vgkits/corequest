from vgkits.story.sack import Sack

class AdventureOver(Exception):
    pass

startEnergy = 2

noChoice = ["Next"]


def completeAdventure(printLines, sack):

    yield from introduceAdventure(printLines, sack)

    yield from binbagAdventure(printLines, sack)

    while sack.friend == None:
        yield from vetAdventure(printLines, sack)

    if sack.friend == "giraffe":
        yield from zooAdventure(printLines, sack)
    elif sack.friend == "hedgehog":
        yield from parkAdventure(printLines, sack)

    yield from busAdventure(printLines, sack) # bus station, hears about cat cafe, boards bus

    yield from shopAdventure(printLines, sack) # finds money, buys one of several different things

    yield from cafeAdventure(printLines, sack) # gets thrown out, has to solve puzzle using thing you bought


def introduceAdventure(printLines, sack):
    printLines(
        "Your name is William and you are a 3 year-old street cat.",
        "You have to find a way to survive another year",
    )
    yield ["Next"]
    printLines(
        "Your energy level is " + str(sack.energy),
        "Don't let your energy get to 0",
        "Else the adventure is over"
    )
    yield ["Next"]
    printLines(
        "You still have all " + str(sack.lives) + " lives",
        "So you can get away with taking some risks"
    )
    yield ["Next"]


def binbagAdventure(printLines, sack):
    inBag = False
    while inBag or (not sack.energy > startEnergy):
        if not inBag:
            printLines(
                "You find yourself in an alley.",
                "You are hungry as always." if sack.energy >= startEnergy else "You are even hungrier!",
                "Something smells interesting.",
                "It's coming from the pile of binbags over there"
            )
            yield ["Climb into a binbag"]
            inBag = True
        else:
            printLines(
                "You are in a binbag.",
                "Do you want to..."
            )
            rubbishLeave = "get out of this smelly bag"
            rubbishDig = "dig deeper into the rubbish"
            rubbishSleep = "sleep here for a while"
            choice = yield [
                *([rubbishDig] if sack.energy < 6 else []),
                rubbishLeave,
                rubbishSleep,
            ]
            if choice == rubbishLeave:
                energyClawBag = 1
                printLines(
                    "You claw your way out of the bag. It's hard work.",
                    "Now clean all the SMELLY GOO off yourself with your tongue",
                    "Eeew!",
                )
                sack.change(energy=-energyClawBag)
                inBag = False
            elif choice == rubbishDig:
                printLines(
                    "You dig to the bottom of the bag",
                    "You find a " + ("HALF-EATEN CAN of TUNA" if sack.energy <= 2 else "MOULDY PORK PIE"),
                    "Delicious!",
                )
                sack.change(energy=+2)
            elif choice == rubbishSleep:
                printLines(
                    "You close your eyes, sleeping so deeply you don't hear",
                    "the sound of the RUBBISH TRUCK approaching.",
                    "The bag is thrown roughly into the crusher",
                    "You fight your way out of the bag but it's too late"
                )
                sack.change(lives=-1)
                inBag = False
            yield ["Continue"]


def vetAdventure(printLines, sack):
    if sack.energy > startEnergy: # both adventures end at vets
        brokenLeg = False
        printLines("Running and caught")
        sack.change(energy=-1)
        yield ["Next"]
    else:
        brokenLeg = True
        printLines("Climbing and fell")
        sack.change(lives=-1)
        yield ["Next"]

    printLines("In the vets")
    yield ["Next"]

    printLines(
        "You are at the vets"
    )
    yield ["Next"]

    if brokenLeg:
        printLines("Vet heals leg")
        yield ["Next"]


    printLines(
        "Choose a friend"
    )
    yield [
        "Giraffe",
        "Hedgehog"
    ]


def parkAdventure(printLines, sack):
    printLines(
        "You are in the park"
    )
    yield ["Next"]


def zooAdventure(printLines, sack):
    printLines(
        "You are at the zoo"
    )
    yield ["Next"]


def busAdventure(printLines, sack):
    printLines(
        "You are at the bus station"
    )
    yield ["Next"]


def shopAdventure(printLines, sack):
    printLines(
        "You are at the shop"
    )
    yield ["Next"]


def cafeAdventure(printLines, sack):
    printLines(
        "You are at the cafe"
    )
    yield ["Next"]


def createAdventure(print, sack):

    sack = Sack()
    sack.energy = startEnergy
    sack.lives = 9

    def printLines(*lines):
        for line in lines:
            print(line)

    def change(**changes):
        for changeItem in changes.items():
            changeKey,changeValue = changeItem
            try:
                # treat numbers as a change
                sack[changeKey] = int(sack[changeKey]) + int(changeValue)

                if changeKey == "lives":
                    assert changeValue == -1, "Unexpected life-changing event" + str(changeItem)
                    print("You just lost a life")
                    if sack.lives == 0:
                        printLines(
                            "You used up all your lives",
                            "Poor William never made it to his 4th birthday"
                        )
                        raise AdventureOver
                    elif sack.lives == 1:
                        printLines(
                            "You've used eight lives",
                            "You can't take any more chances",
                            "Die again and your adventure will be over"
                        )
                    else:
                        printLines("You have " + str(sack.lives) + " left")
                elif changeKey == "energy":
                    if changeValue < 0:
                        if sack.energy <= 0:
                            printLines(
                                "You ran out of energy.",
                                "William closes his eyes and falls into ",
                                "a deep sleep for the last time",
                            )
                            raise AdventureOver
                        else:
                            printLines(
                                "You used " + str(abs(changeValue)) + " energy.",
                                "leaving just " + str(sack.energy) + " left."
                            )
                    elif changeValue > 0:
                        printLines(
                            "You gained " + str(abs(changeValue)) + " energy",
                            "giving you a total energy of " + str(sack.energy)
                        )
            except TypeError:
                sack[changeKey] = changeValue

    sack.change = change

    try:
        yield from completeAdventure(printLines, sack)
    except AdventureOver:
        pass

    print("Your adventure is over")
    yield ["Finish"]


if __name__ == "__main__":
    from vgkits.story.adaptor import webSequenceAdaptor as sequenceAdaptor
    from vgkits.console.webConsole import hostGame
    createLifeSequence = sequenceAdaptor(createAdventure)
    hostGame(createLifeSequence)
