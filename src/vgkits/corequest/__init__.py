class WebException(Exception):
    status = b"500 Internal Server Error"


class BadRequestException(WebException):
    status = b"400 Bad Request"


class NotFoundException(WebException):
    status = b"404 Not Found"


# TODO standardise single extractParams with separator args

def extractParams(query):
    """Splits key-value pairs in GET query strings, POST form-urlencoded bodies"""
    params = {}
    paramPairs = query.split(b"&")
    for paramPair in paramPairs:
        paramName, paramValue = paramPair.split(b"=")
        params[paramName] = paramValue
    return params


def extractCookies(cookieHeaderValue):
    """Splits key-value pairs in Cookie headers"""
    cookies = {}
    cookiePairs = cookieHeaderValue.split(b";")
    for cookiePair in cookiePairs:
        cookieName, cookieValue = cookiePair.strip().split(b"=")
        cookies[cookieName] = cookieValue
    return cookies


def createHeaderReceiver(map, debug=False):
    """Factory for a generator which accepts HTTP headers line by line via send()
    extracting GET and POST method, path, resource, param and cookie keypairs.
    Generator returns a map of extracted values"""
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
                    map.update(
                        method=method,
                        path=path,
                    )
                    if method == b"GET" and b"?" in path:
                        resource, query = path.split(b"?")
                        map.update(resource=resource)
                        map.update(params=extractParams(query))
                    else:
                        map.update(resource=path)
                elif line.startswith(b"Cookie:"):
                    _, cookieHeaderValue = line.split(b":")
                    map.update(cookies=extractCookies(cookieHeaderValue))
                elif line.startswith(b"Content-Type:"):
                    contentType = line.split(b":")[-1]
                    map.update(contentType=contentType)
                elif line.startswith(b"Content-Length:"):
                    contentLength = line.split(b":")[-1]
                    contentLength = int(contentLength)  # TODO limit contentLength (defeat DOS?)
                    map.update(contentLength=contentLength)
                elif line.startswith(b"Purpose: prefetch"):
                    map.update(prefetch=True)
            except ValueError:
                pass

    return map


def createBodyReceiver(map, debug=False):
    if map["method"] == b"POST":
        if (map["contentLength"] > 0 and
                b"application/x-www-form-urlencoded" in map["contentType"]):
            postBody = yield  # consume body content for keypairs
            if debug:
                print(postBody)
            map.update(params=extractParams(postBody))
        else:
            raise BadRequestException("POST not x-www-form-urlencoded")


def createReadReceiver(map, debug=False):
    headerReceiver = createHeaderReceiver(map, debug)
    try:
        headerReceiver.send(None)  # run lines until yield
        while True:
            line = yield None  # request line of bytes
            headerReceiver.send(line)
    except StopIteration as e:
        pass  # reached end of headers

    bodyReceiver = createBodyReceiver(map, debug)
    try:
        bodyReceiver.send(None)  # raise StopIteration, unless receiver yields (requesting bytes)
        body = yield map["contentLength"]  # request body bytes
        bodyReceiver.send(body)
    except StopIteration as e:
        pass

    return map



