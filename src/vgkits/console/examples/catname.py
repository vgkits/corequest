firstNames = ['Smokey', 'Princess', 'Buddy', 'Dusty', 'Charlie', 'Rusty', 'Oliver', 'Felix', 'Monty', 'Taz', 'Buster',
              'Simba', 'Pepper', 'Oreo', 'Casper', 'Oscar', 'Milo', 'Kitty', 'Missy', 'Maggie', 'Bella',
              'Molly', 'Sooty', 'Patch', 'Shadow', 'Cleo']

secondNames = ['Jake', 'Boots', 'Angel', 'Samantha', 'Whiskers', 'Thomas', 'Tiger', 'Gizmo', 'Max', 'Rocky', 'Lucy',
               'Misty', 'Midnight', 'Toby', 'Ginger', 'Fluffy', 'Daisy', 'Baby', 'Lucky', 'Pumpkin', 'Jack', 'Sammy',
               'Sassy', 'Sylvester', 'Spike', 'Precious']


def alphabetPosition(name):
    return ord(name[0].lower()) - ord('a')


def createSequence(print):
    userGiven = ""
    userFamily = ""
    while len(userGiven) == 0:
        userGiven = yield "Enter your given name (christian name): "
    while len(userFamily) == 0:
        userFamily = yield "Enter your family name (surname): "
    print(
        "Your CAT NAME is",
        firstNames[alphabetPosition(userGiven) % len(firstNames)],
        secondNames[alphabetPosition(userFamily) % len(secondNames)],
    )
    yield "Press enter to continue: "


def run():
    from vgkits.console.textConsole import hostGame
    hostGame(createSequence)


if __name__ == "__main__":
    while True:
        run()
