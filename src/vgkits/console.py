from vgkits.corequest import *

htmlHead = b"""
<!DOCTYPE html>
<html>
    <head>
        <title>Example page</title>
        <style>
            pre {
                overflow-x: auto;
                white-space: pre-wrap;
                white-space: -moz-pre-wrap;
                white-space: -pre-wrap;
                white-space: -o-pre-wrap;
                word-wrap: break-word;
            }
        </style>
        <meta charset='utf-8'>
    </head>
    <body>"""
htmlPreOpen = b"""<pre>"""
htmlPreClose = b"""</pre>"""
htmlResetForm = b"""<form method="POST" style="position:absolute; top:0px; right:0px" autocomplete="off"><button type="submit" name="reset" value="true">X</button></form>"""
htmlResponseForm = b"""<form method="POST" autocomplete="off"><input type="text" name="response" autofocus></form>"""
htmlBreak = b"<br/>"
htmlFoot = b"""
    </body>
</html>
"""

crlf = b"\r\n"


# original from https://gitlab.com/superfly/dawndoor/blob/master/src/dawndoor/web.py
def decodeuricomponent(string):
    string = string.replace('+', ' ')
    arr = string.split('%')
    arr2 = [chr(int(part[:2], 16)) + part[2:] for part in arr[1:]]
    return arr[0] + ''.join(arr2)


def writeHttpHeaders(cl, status=b"200 OK", contentType=b"text/html", charSet=b"UTF-8"):
    if type(status) is not bytes:
        status = str(status).encode('utf-8')
    cl.send(b"HTTP/1.1 ")
    cl.send(status)
    cl.send(crlf)
    cl.send(b"Content-Type:")
    cl.send(contentType)
    cl.send(b" ; charset=")
    cl.send(charSet)
    cl.send(crlf)
    cl.send(b"Connection: close")
    cl.send(crlf)


def writeCookieHeaders(cl, requestMap):
    cookies = requestMap.get("cookies")
    if cookies is not None:
        cl.send(b"Set-Cookie: ")
        comma = False
        for cookieName, cookieValue in cookies.items():
            if comma:
                cl.send(b",")
            cl.send(cookieName)
            cl.send(b"=")
            cl.send(cookieValue)
            comma = True
        cl.send(crlf)


def writeHtmlBegin(cl):
    cl.send(htmlHead)
    cl.send(htmlResetForm)
    cl.send(htmlPreOpen)


def writeHtmlEnd(cl):
    cl.send(htmlPreClose)
    cl.send(htmlResponseForm)
    cl.send(htmlFoot)


def writeItem(cl, obj):
    cl.send(str(obj).encode('utf-8'))


gameMap = {}


def resetAllGames():
    global gameMap
    gameMap = {}


def getGame(cookie):
    return gameMap.get(cookie)


def setGame(cookie, value):
    if value is None:
        gameMap.pop(cookie, None)
    else:
        gameMap[cookie] = value
    return value


def createRequestCoroutine(createSequence, repeat=True, resetAll=True, debug=False):
    if resetAll:
        resetAllGames()

    cl = None  # doprint references this current client socket reference

    def doprint(*items, sep=b" ", end=b"\n"):
        """Equivalent to print, but writes to current client socket """
        if type(sep) is str:
            sep = sep.encode('utf-8')
        if type(end) is str:
            end = end.encode('utf-8')
        if end == b"\n":
            end = htmlBreak
        try:
            prev = None
            for item in items:
                if prev is not None:
                    cl.send(sep)
                itemType = type(item)
                if itemType is str:  # TODO entity encode strings?
                    item = item.encode('utf-8')
                elif itemType is bytes:
                    pass  # send bytestrings unencoded
                else:
                    raise Exception(
                        'Cannot coerce {} to bytes'.format(itemType))
                cl.send(item)
                prev = item
            cl.send(end)
        except OSError as e:
            print(str(e))

    while True:
        cl, requestMap = yield

        try:
            if debug:
                print(requestMap)

            if requestMap is None or requestMap == {}:
                raise WebException("Request empty")

            resource = requestMap.get('resource')

            sessionCookie = getSessionCookie(requestMap)

            reset = sessionCookie is None

            if resource == b"/":

                # process application state, render page

                game = getGame(sessionCookie)

                method = requestMap.get('method')
                params = requestMap.get('params')

                # reset logic
                if method == b"GET":
                    if game is None:
                        reset = True
                    else:  # interactions with running game are all HTTP POST
                        raise BadRequestException(
                            "In-progress game: GET request invalid")
                elif method == b"POST":
                    if params is not None:
                        if b"reset" in params:
                            reset = True

                if reset:
                    if sessionCookie is not None:
                        setGame(sessionCookie, None)
                    sessionCookie = lazyCreateSessionCookie(requestMap)
                    game = setGame(sessionCookie, createSequence(doprint))
                else:
                    game = getGame(sessionCookie)
                    if game is None:
                        raise BadRequestException(
                            "In-progress game not available")

                response = None
                if method == b"POST" and not reset:
                    if params is not None:
                        response = params.get(b"response")
                    if response is not None:
                        response = response.decode("utf-8")
                        response = decodeuricomponent(response)
                    elif not reset:
                        raise BadRequestException(
                            "In-progress game: POST without 'response' param invalid")

                writeHttpHeaders(cl)

                if reset:
                    writeCookieHeaders(cl, requestMap)

                cl.send(crlf)  # finish headers

                writeHtmlBegin(cl)

                if debug:
                    doprint(str(requestMap))

                promptAttempts = 0
                while True:
                    try:
                        promptAttempts += 1
                        # coroutine calls doprint closure on cl.send()
                        prompt = game.send(response)
                        writeItem(cl, prompt)
                        cl.send(htmlBreak)
                        break
                    except StopIteration:
                        if repeat:  # create and run the game again
                            if promptAttempts <= 1:
                                game = setGame(
                                    sessionCookie, createSequence(doprint))
                                response = None
                                continue
                            else:
                                raise Exception("Game offered no prompts")
                        else:
                            cl.send(b"Game Over. Server closing")
                            break

                writeHtmlEnd(cl)
                continue

            else:  # unknown resource
                raise NotFoundException("Unknown resource ", resource)

        except Exception as e:  # intercept and write error page
            if isinstance(e, WebException):
                writeHttpHeaders(cl, status=e.status)
            else:
                writeHttpHeaders(cl, status=WebException.status)
            writeHtmlBegin(cl)
            cl.send(b"Error: ")
            if isinstance(e, WebException):
                cl.send(e.status)
            cl.send(htmlBreak)
            writeItem(cl, repr(e))
            cl.send(htmlBreak)
            cl.send(b"Reset session with X at top-right of this page")
            writeHtmlEnd(cl)
            raise
        finally:
            cl = None


def syncHostGame(createSequence, port=8080, debug=False):
    from vgkits.corequest.syncRequests import serveSyncRequests
    requestCoroutine = createRequestCoroutine(createSequence, repeat=True, resetAll=True, debug=debug)

    def syncRequestHandler(cl, requestMap):
        try:
            requestCoroutine.send((cl, requestMap))
        except StopIteration:
            pass

    serveSyncRequests(syncRequestHandler, port, debug)


async def asyncHostGame(createSequence, port=8080, debug=False):
    from vgkits.corequest.async import serveAsyncRequests
    requestCoroutine = createRequestCoroutine(createSequence, repeat=True, resetAll=True, debug=debug)

    async def asyncRequestHandler(cl, requestMap):
        try:
            requestCoroutine.send((cl, requestMap))
        except StopIteration:
            pass

    await serveAsyncRequests(asyncRequestHandler, port, debug)


def run():
    def createSequence(print):
        print("Welcome to the game")
        username = yield "What is your name? "
        print("Hello " + username)
        yield "Press enter to restart the game "

    syncHostGame(createSequence)


if __name__ == "__main__":
    run()
