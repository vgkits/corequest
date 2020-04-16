
Establish a vgkits-console pypi project

Define a vgkits-console-example repo which can be used to mirror the Heroku Python 'getting started' tutorial

Deploy some of Sky Molly's code to Heroku as a demonstration of homeschooling, using the example repo

Consider Gunicorn to coordinate with async / asyncio implementations

Consider convergence between mapSyncHandler and WSGI (python servlet-like) invocations...

```py
def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    yield b'Hello, World\n'
```

Would permit hosting via 
- Heroku
- PythonAnywhere
- Google App Engine's webapp2
- Lambda? ( https://www.missioncloud.com/blog/going-serverless-with-python-wsgi-apps )
- ESP8266 - with my own 'WSGI' handler

Possible name `wsgish`
Track https://github.com/adafruit/Adafruit_CircuitPython_WSGI
Look into being able to run console apps on Adafruit_CircuitPython

Configure play.vgkits.org with these domain name servers

ns-1671.awsdns-16.co.uk
ns-102.awsdns-12.com
ns-1188.awsdns-20.org
ns-936.awsdns-53.net


Short term:
Merge host-web-console branch back into master
Write an intro 'Generator wrapper' for webConsole that explains the Cross in the corner, and points to the project and source
Complete basic documentation within the project README.md structure
Ensure i spy and hangman examples are good ones
Add a logging wrapper around the server, so that sessions are recorded to text

Decide on a name and distribute as a pypi package installable via PIP
Create a docker image that pulls in the pip package, launches the server, exposes the port
Host the docker image on an EC2, (in the future routed through Nginx, to allow the EC2 to handle other domains/paths' traffic?)
- Possibly through lightsail (1 month)
- https://cloud.google.com/kubernetes-engine
Create a DNS alias - maybe console.vgkits.org
Create a WSGI adapter (prototyped through gunicorn) that generates a requestMap from a WSGI call enabling hosting on...
- Heroku
- Cloud Run
- PythonAnywhere
- Lambda
- Others with gunicorn/wsgi support?
Share the project with the Adafruit WSGI people
Set up a route over home broadband to a version running on an ESP8266
Configure an APIGateway route via Proxying to the ESP8266 (allowing alarms?)
Write a quiz game

Fix the case that hangman phrases need you to guess punctuation! e.g. it's needs a guess of '