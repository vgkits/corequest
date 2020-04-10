from vgkits import corequest
import unittest

from vgkits.agnostic import asyncio


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

    def testStartsReadingHeaders(self):
        try:
            headerReceiver = corequest.createHeaderReceiver(requestMap={})
            headerReceiver.send(None)
        except StopIteration:
            self.fail("headerReceiver didn't start reading")
        else:
            pass

    def testStopsAfterHeaders(self):
        try:
            headerReceiver = corequest.createHeaderReceiver(requestMap={})
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
        requestMap = corequest.mapFile(mockFile)
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
            requestMap = await corequest.mapStream(mockStream)
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


"""TODO CH 
Add synchronous socket test
    Implement Asynchronous mapSocketAsync and mapStreamAsync functions
"""
