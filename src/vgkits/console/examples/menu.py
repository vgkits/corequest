names = (
    "Hello World",
    "Cat Name",
    "I Spy",
    "Consequences",
    "Math Dice",
    "Hangman",
    "Chat",
)

lastChoice = None


def menuSequence(print):
    global lastChoice

    print("The following games are available:")
    print()
    for name in names:
        print(name)
    print()

    if lastChoice is None:
        choice = yield "Type the name you want and press ENTER: "
    else:
        choice = yield "Type the name you want or leave blank to run " + lastChoice + " :"
        if choice == "":
            choice = lastChoice

    choice = choice.lower()  # make lowercase
    choice = choice.replace(" ", "")  # remove spaces

    if choice == "helloworld":
        from vgkits.console.examples.helloworld import createSequence
    elif choice == "catname":
        from vgkits.console.examples.catname import createSequence
    elif choice == "ispy":
        from vgkits.console.examples.ispy import createSequence
    elif choice == "consequences":
        from vgkits.console.examples.consequences import createSequence
    elif choice == "mathdice":
        from vgkits.console.examples.mathdice import createSequence
    elif choice == "hangman":
        from vgkits.console.examples.hangman import createSequence
    elif choice == "chat":
        from vgkits.console.examples.chat import createSequence
    else:
        yield "No game matching '" + choice + "'. Press ENTER"
        return

    lastChoice = choice

    sequence = createSequence(print)
    yield from sequence


def run():
    from vgkits.console.textConsole import hostGame
    hostGame(menuSequence)


if __name__ == "__main__":
    while True:
        run()
