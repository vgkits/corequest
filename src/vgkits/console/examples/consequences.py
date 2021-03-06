from time import sleep


def createSequence(print):
    manAdjective = yield "Write an adjective (describing word) for a man? "
    manName = yield "Write a name for a man? "
    womanAdjective = yield "Write an adjective (describing word) for a woman? "
    womanName = yield "Write a name for a woman? "
    placeName = yield "Where were they? "
    placeReason = yield "Why were they there? "
    manWearing = yield "What was the man wearing? "
    womanWearing = yield "What was the woman wearing? "
    manSaid = yield "What did the man say? "
    womanSaid = yield "What did the woman say? "
    consequences = yield "What were the consequences? "
    print(
        manAdjective, manName,
        "met", womanAdjective, womanName,
        "at", placeName,
        "to", placeReason
    )
    sleep(0.5)
    print(manName, "wore", manWearing)
    sleep(0.5)
    print(womanName, "wore", womanWearing)
    sleep(0.5)
    print(manName, "said", manSaid)
    sleep(0.5)
    print(womanName, "said", womanSaid)
    sleep(0.5)
    print("...and the consequences were", consequences)
    print()
    yield "Press ENTER to exit the game"


def run():
    from vgkits.console.textConsole import hostGame
    hostGame(createSequence)


if __name__ == "__main__":
    run()
