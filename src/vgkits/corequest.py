class WebException(Exception):
    status = b"500 Internal Server Error"


class BadRequestException(WebException):
    status = b"400 Bad Request"


class NotFoundException(WebException):
    status = b"404 Not Found"


def extractParams(query):
    params = {}
    paramPairs = query.split(b"&")
    for paramPair in paramPairs:
        paramName, paramValue = paramPair.split(b"=")
        params[paramName] = paramValue
    return params


def extractCookies(cookieHeaderValue):
    cookies = {}
    cookiePairs = cookieHeaderValue.split(b";")
    for cookiePair in cookiePairs:
        cookieName, cookieValue = cookiePair.strip().split(b"=")
        cookies[cookieName] = cookieValue
    return cookies


def createHeaderReceiver(requestMap, debug=False):
    """Factory for a generator which accepts HTTP headers line by line via send()
    extracting GET and POST method, path, resource, param and cookie keypairs.
    Generator returns a dict of extracted values"""
    while True:
        line = yield  # consider making lowercase before processing
        if debug:
            print(line)
        if not line or line == b'\r\n':
            break
        else:
            try:
                if line.startswith(b"GET") or line.startswith(b"POST"):
                    (method, path, version) = line.split()
                    requestMap.update(
                        method=method,
                        path=path,
                    )
                    if method == b"GET" and b"?" in path:
                        resource, query = path.split(b"?")
                        requestMap.update(resource=resource)
                        requestMap.update(params=extractParams(query))
                    else:
                        requestMap.update(resource=path)
                elif line.startswith(b"Cookie:"):
                    _, cookieHeaderValue = line.split(b":")
                    requestMap.update(cookies=extractCookies(cookieHeaderValue))
                elif line.startswith(b"Content-Type:"):
                    contentType = line.split(b":")[-1]
                    requestMap.update(contentType=contentType)
                elif line.startswith(b"Content-Length:"):
                    contentLength = line.split(b":")[-1]
                    contentLength = int(contentLength)  # TODO limit contentLength (defeat DOS?)
                    requestMap.update(contentLength=contentLength)
                elif line.startswith(b"Purpose: prefetch"):
                    requestMap.update(prefetch=True)
            except ValueError:
                pass

    return requestMap


def createBodyReceiver(requestMap, debug=False):
    if requestMap["method"] == b"POST":
        if (requestMap["contentLength"] > 0 and
                b"application/x-www-form-urlencoded" in requestMap["contentType"]):
            postBody = yield  # consume body content for keypairs
            if debug:
                print(postBody)
            requestMap.update(params=extractParams(postBody))
        else:
            raise BadRequestException("POST not x-www-form-urlencoded")


def mapSocketSync(clientSocket, debug=False):
    """Consumes bytes from clientSocket interpreting them
    as lines of a HTTP request. Returns a map describing
    the request.
    """
    clientFile = clientSocket.makefile('rb', 0)
    try:
        return mapFile(clientFile, debug)
    finally:
        import sys
        if hasattr(sys, 'implementation'):  # mpy or py3
            name = sys.implementation.name
            if name == "micropython" or name == "circuitpython":
                pass  # s.makefile() was a no-op, closing file will close socket
            else:
                clientFile.close()  # file created above should be closed


def createReadReceiver(requestMap, debug=False):
    headerReceiver = createHeaderReceiver(requestMap, debug)
    try:
        headerReceiver.send(None)  # run lines until yield
        while True:
            line = yield None  # request line of bytes
            headerReceiver.send(line)
    except StopIteration as e:
        pass  # reached end of headers

    bodyReceiver = createBodyReceiver(requestMap, debug)
    try:
        bodyReceiver.send(None)  # raise StopIteration, unless receiver yields (requesting bytes)
        body = yield requestMap["contentLength"]  # request body bytes
        bodyReceiver.send(body)
    except StopIteration as e:
        pass

    return requestMap


def receiveFile(file, readReceiver):
    """See also receiveStream"""
    try:
        count = readReceiver.send(None)  # run to first yield
        while True:
            if count is None:
                count = readReceiver.send(file.readline())
            else:
                count = readReceiver.send(file.read(count))
    except StopIteration:
        pass


def mapFile(file, debug=False):
    requestMap = dict()
    readReceiver = createReadReceiver(requestMap, debug)
    receiveFile(file, readReceiver)
    return requestMap


async def receiveStream(stream, readReceiver):
    """See also receiveFile"""
    try:
        count = readReceiver.send(None)  # run to first yield
        while True:
            if count is None:
                count = readReceiver.send((await stream.readline()))
            else:
                count = readReceiver.send((await stream.read(count)))
    except StopIteration:
        pass


async def mapStream(stream, debug=False):
    requestMap = dict()
    readReceiver = createReadReceiver(requestMap, debug)
    await receiveStream(stream, readReceiver)
    return requestMap
