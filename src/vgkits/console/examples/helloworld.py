def createSequence(print):
    print("Welcome to the game")
    username = yield "What is your name? "
    print("Hello " + username)
    yield "Press enter to restart the game "


def run():
    from vgkits.console.textConsole import hostGame
    hostGame(createSequence)


if __name__ == "__main__":
    run()
