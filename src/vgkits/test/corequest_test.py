import unittest
import socket
import pickle
from time import sleep

from vgkits.agnostic import asyncio
from vgkits import corequest
from vgkits.corequest.syncRequests import mapFile, serveSyncRequests
from vgkits.corequest.asyncRequests import mapStream


def mapHeaders(*lines):
    requestMap = {}
    headerReceiver = corequest.createHeaderReceiver(requestMap)
    try:
        headerReceiver.send(None)
        for line in lines:
            headerReceiver.send(line)
    except StopIteration:
        pass
    return requestMap


def runAsyncTest(asyncTestFun):
    def handle_exception(loop, context):
        exc = context.get("exception", context["message"])
        raise exc

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)
    asyncHandle = asyncTestFun()
    loop.run_until_complete(asyncHandle)
    loop.close()


class MockFileSync:
    def __init__(self, *lines):
        self.lines = lines
        self.resetLines()

    def resetLines(self):
        self.lineSequence = (line for line in self.lines)

    def readline(self):
        if self.lineSequence is not None:
            try:
                line = next(self.lineSequence)
                return line
            except StopIteration:
                self.lineSequence = None
        return ""

    def read(self, byteCount):
        line = self.readline()
        if len(line) == byteCount:
            return line
        else:
            raise Exception("Line isn't {} long".format(byteCount))


class MockStreamAsync:
    def __init__(self, lines):
        self.lines = lines

    def __init__(self, *lines):
        self.lines = lines
        self.resetLines()

    def resetLines(self):
        self.lineSequence = (line for line in self.lines)

    async def readline(self):
        await asyncio.sleep(0.01)
        if self.lineSequence is not None:
            try:
                line = next(self.lineSequence)
                return line
            except StopIteration:
                self.lineSequence = None
        return ""

    async def read(self, byteCount):
        await asyncio.sleep(0.01)
        line = await self.readline()
        if len(line) == byteCount:
            return line
        else:
            raise Exception("Line isn't {} long".format(byteCount))


class TestExtractParams(unittest.TestCase):

    def testOneParam(self):
        self.assertEqual(
            corequest.extractParams(b"hello=world"),
            {b"hello": b"world"}
        )

    def testTwoParams(self):
        self.assertEqual(
            corequest.extractParams(b"hello=world&yo=mars"),
            {
                b"hello": b"world",
                b"yo": b"mars"
            }
        )


class TestExtractCookies(unittest.TestCase):
    def testOneCookie(self):
        self.assertEqual(
            corequest.extractCookies(b"hello=world"),
            {b"hello": b"world"}
        )

    def testTwoCookies(self):
        self.assertEqual(
            corequest.extractCookies(b"hello=world;yo=mars"),
            {
                b"hello": b"world",
                b"yo": b"mars"
            }
        )


class TestHeaderReceiver(unittest.TestCase):

    def testReceiverStarts(self):
        try:
            headerReceiver = corequest.createHeaderReceiver(map={})
            headerReceiver.send(None)
        except StopIteration:
            self.fail("headerReceiver didn't start reading")
        else:
            pass

    def testReceiverStops(self):
        try:
            headerReceiver = corequest.createHeaderReceiver(map={})
            headerReceiver.send(None)
            headerReceiver.send(b"\r\n")
        except StopIteration:
            pass
        else:
            self.fail("headerReceiver didn't stop reading")

    def testGet(self):
        requestMap = mapHeaders(
            b"GET /hello.html HTTP/1.1\r\n",
            b"\r\n"
        )
        self.assertEqual(requestMap, {
            "method": b"GET",
            "resource": b"/hello.html",
            "path": b"/hello.html",
        })

    def testGetWithParams(self):
        requestMap = mapHeaders(
            b"GET /hello.html?hello=world&yo=mars HTTP/1.1\r\n",
            b"\r\n"
        )
        self.assertEqual(requestMap, {
            "method": b"GET",
            "resource": b"/hello.html",
            "path": b"/hello.html?hello=world&yo=mars",
            "params": {
                b"hello": b"world",
                b"yo": b"mars",
            }
        })

    def testGetWithCookieHeader(self):
        requestMap = mapHeaders(
            b"GET /hello.html HTTP/1.1\r\n",
            b"Cookie: hello=world;yo=mars\r\n",
            b"\r\n"
        )
        self.assertEqual(requestMap, {
            "method": b"GET",
            "resource": b"/hello.html",
            "path": b"/hello.html",
            "cookies": {
                b"hello": b"world",
                b"yo": b"mars",
            }
        })


class TestBodyReceiver(unittest.TestCase):

    def testPostedParams(self):
        requestMap = {
            "method": b"POST",
            "contentType": b"application/x-www-form-urlencoded",
            "contentLength": 19
        }
        bodyReceiver = corequest.createBodyReceiver(requestMap)
        try:
            bodyReceiver.send(None)
            bodyReceiver.send(b"hello=world&yo=mars")
        except StopIteration:
            pass
        self.assertEqual(requestMap["params"], {
            b"hello": b"world",
            b"yo": b"mars",
        })


class TestFileSync(unittest.TestCase):

    def testPostWithEncodedParams(self):
        mockFile = MockFileSync(
            b"POST /hello.html HTTP/1.1\r\n",
            b"Content-Type:application/x-www-form-urlencoded\r\n",
            b"Content-Length:19\r\n",
            b"\r\n",
            b"hello=world&yo=mars",
        )
        requestMap = mapFile(mockFile)
        self.assertEqual(requestMap, {
            "method": b"POST",
            "resource": b"/hello.html",
            "path": b"/hello.html",
            "contentType": b"application/x-www-form-urlencoded\r\n",
            "contentLength": 19,
            "params": {
                b"hello": b"world",
                b"yo": b"mars",
            }
        })


class TestStreamAsync(unittest.TestCase):
    def testPostWithEncodedParamsAsync(self):
        async def asyncTest():
            mockStream = MockStreamAsync(
                b"POST /hello.html HTTP/1.1\r\n",
                b"Content-Type:application/x-www-form-urlencoded\r\n",
                b"Content-Length:19\r\n",
                b"\r\n",
                b"hello=world&yo=mars",
            )
            requestMap = await mapStream(mockStream)
            self.assertEqual(requestMap, {
                "method": b"POST",
                "resource": b"/hello.html",
                "path": b"/hello.html",
                "contentType": b"application/x-www-form-urlencoded\r\n",
                "contentLength": 19,
                "params": {
                    b"hello": b"world",
                    b"yo": b"mars",
                }
            })

        return runAsyncTest(asyncTest)


class TestSocketSync(unittest.TestCase):
    def testClientSocket(self):  # TODO CH refactor as contextManager?
        def makeRequest(lines, callback, port=8080):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect((socket.gethostname(), port))
                requestFile = s.makefile('rwb')
                try:
                    requestFile.writelines(lines)
                    requestFile.flush()
                    callback(requestFile)
                finally:
                    requestFile.close()  # needs to be different on micropython?
            finally:
                s.close()

        launched = False
        # Spawn server in its own thread
        def notifyServer(addr, port):
            nonlocal launched
            launched = True

        def pickleServer():
            def pickleMapHandler(requestSocket, requestMap):
                responseFile = requestSocket.makefile('wb')
                pickle.dump(requestMap, responseFile)
                responseFile.flush()
                responseFile.close()
                raise KeyboardInterrupt # terminate server after handling client
            try:
                serveSyncRequests(pickleMapHandler, cb=notifyServer)
            except KeyboardInterrupt:
                pass

        import threading
        serverThread = threading.Thread(target=pickleServer)
        serverThread.start()

        def checkResponse(responseFile):
            loaded = pickle.load(responseFile)
            self.assertEqual(
                loaded,
                {
                    "method": b"GET",
                    "resource": b"/hello.html",
                    "path": b"/hello.html",
                    "cookies": {
                        b"hello": b"world",
                        b"yo": b"mars",
                    }
                }
            )

        # Run client in this thread, check server response
        while not launched:
            sleep(0)
            pass
        makeRequest([
            b"GET /hello.html HTTP/1.1\r\n",
            b"Cookie: hello=world;yo=mars\r\n",
            b"\r\n"
        ], checkResponse)


"""TODO CH 
    Add socket tests, one sync test, the other async
    Port through server implementations 
        - generator-based webConsole 
        - gzipped webrepl
"""
