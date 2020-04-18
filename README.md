# CoRequest

CoRequest is a python3 and micropython project making it easy to host multi-stage text-input 
interactions in a a text console or a webpage.

The [simplest example](https://github.com/vgkits/corequest/blob/master/src/vgkits/console/examples/helloworld.py) of a 
text-based game looks like this...

```py
def createSequence(print):
    print("Welcome to the game")
    username = yield "What is your name? "
    print("Hello " + username)
    yield "Press enter to restart the game "
```

More examples of text games written in CoRequest are at http://play.vgkits.org

# Core Principles 

Calls to `print()` make lines of text appear on screen. 
Lines with `yield` prompt the user for input, pausing the running of your game until they enter something.

Games authored in this way can be hosted in a text console, or [served as a webpage](https://github.com/vgkits/corequest/blob/master/src/vgkits/console/examples/helloweb.py).

When published as a webpage, calls to `print()` add lines of text to the page. 
Lines with `yield` causes the page to be finalised and sent to the user, including an input box to await their response.

The play.vgkits.org server runs python 3, but can also run in Micropython, like...

```
micropython -m vgkits.console.webConsole
```

# Complex Example

A more complex example is shown below, which implements a [playable 'I Spy' guessing game](https://github.com/vgkits/corequest/blob/master/src/vgkits/console/examples/ispy.py). You can play this game and others via the web at http://play.vgkits.org


```py
spiedLists = {
    "at the zoo": [
        "elephant",
        "zebra",
    ],
    "at the seaside": [
        "shell",
        "sandcastle",
    ],
}

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
```

# Advanced

An example for advanced learners is shown below. It demonstrates how a [functional chatroom](https://github.com/vgkits/corequest/blob/master/src/vgkits/console/examples/chat.py) can be implemented in a handful of lines of code. 

You can play this game and others via the web at http://play.vgkits.org 

```py
posts = list()

def createSequence(print):

    # store this session user's name
    myname = yield "What is your name? "
    print("Welcome to the chatroom, " + myname)

    while True:
        # show post history
        for name, message in posts:
            print("<b><i>", name, "</i></b>", message)

        # ask for next post
        print("")
        mymessage = yield "Type your message or press enter to refresh"

        # handle the post
        if mymessage is not "":
            mypost = (myname, mymessage)
            posts.append(mypost)

        posts[:] = posts[-10:] # keep only the last 10 posts
```

The way this chatroom shares posts between multiple users accessing it from different browsers is a fantastic starting point for all kinds of computing education. N.B. it should be locally hosted for safety, or hosted at an obfuscated URL not published to anyone as it deliberately demonstrates web security issues. 

Among the subjects which can be explored using this demonstration...
* How do we know if anyone is who they say they are on the internet?
    - exercise: invite the class to the chatroom, log on yourself with a previously-used name
* Why do we need usernames and passwords?
    - exercise: add code for users to secure their accounts with passwords
* How does user and session management on the web really work? 
    - host the chatroom with debug=True to dump every web request
* Why does user input need escaping to prevent Cross-Site-Scripting?
    - users can write HTML, CSS and Javascript directly into the page and see the results - this is bad and should be stopped :)
* How are characters (letters, numbers) encoded?
    - users can type in HTML Entity codes to choose ASCII codes, or Unicode Emojis! 
* What is the use of XMLHttpRequest
    - advanced exercise - update the page when there's a new post available

# Background 

This project helps novices to program complex, multi-step user interactions
in the simplest possible way. 

An original focus of the project was the creation of Web UIs to control 
embedded micropython projects, with simple UI and hardware functions running 
concurrently.

There are four layers to the generator logic of a running co-request program. Generators and coroutines are used for...

* Novice programmers to design their user interfaces and games in just a few lines of code
* HTTP request parsing - coroutine logic for processing HTTP request lines from a client within either a sync or async loop 
* Client Session handoff - handoff to a 'stateful' coroutine serving client requests against prenegotiated sessions
* Web templating - coroutines sending back atomic blocks of response bytes using page templating logic against a client request

Novice developers building a web UI will see just one of the layers - the generators they write
which are then invoked by passing them to `hostGame()`. The layers below can be investigated and 
specialised by more advanced developers. 

Under the hood, three further layers of coroutine generators...
1. `send()` HTTP request lines (from a blocking/async socket) to generate a requestMap
    - fills the role of python's WSGI, also parses cookies and GET or POST parameters
2. `send()` requestMaps handed off to a session coroutine
    - use of the coroutine pattern allows either sync or async server accept
3. `yield` HTTP response lines to be sent through a blocking or async socket back to the user 
    - confession: this layer will soon be refactored to use python yield syntax. Currently it uses callbacks to a write function