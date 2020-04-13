from vgkits.console.examples.helloworld import createSequence

def run():
    from vgkits.console.webConsole import hostGame
    hostGame(createSequence)

if __name__ == "__main__":
    run()