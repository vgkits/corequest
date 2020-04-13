from vgkits import random

# support alternative values
# ("streetlight", "streetlamp"),
# ("bicycle", "bike"),

spiedLists = {
    "at the zoo": [
        "rhino",
        "elephant",
        "zebra",
        "monkey",
        "giraffe",
        "gorilla",
        "meerkat",
        "flamingo",
        "lion",
        "cheetah",
        "tiger",
    ],
    "at the seaside": [
        "sand",
        "sea",
        "sky",
        "shell",
        "rocks",
        "pebble",
        "ocean",
        "pond",
        "sandcastle",
        "waves",
    ],
    "in the house": [
        "kitchen",
        "door",
        "window",
    ],
    "in the street": [
        "shop",
        "sign",
        "car",
        "road",
        "stall",
        "cafe",
        "street",
        "mall",
    ]}

locations = list(spiedLists.keys())

def createSequence(print):
    location = random.pick(locations)
    spiedList = spiedLists[location]
    spied = random.pick(spiedList)
    spiedMatch = spied.lower().replace(" ", "")

    while True:
        print("I am", location.upper())
        print("I spy with my little eye, something beginning with...", spied[0].upper())
        guess = yield "Type a word then press ENTER. Leave blank and press ENTER to give up"

        guess = guess.lower().replace(" ", "")
        if guess == spiedMatch:
            print("You guessed it!")
            break
        if guess == "":
            print("You gave up")
            break

        print("No. The word is not", guess)

    print("The word is", spied)
    yield "Press ENTER to continue: "


def run():
    from vgkits.console.textConsole import hostGame
    hostGame(createSequence)


if __name__ == "__main__":
    while True:
        run()
