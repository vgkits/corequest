
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

