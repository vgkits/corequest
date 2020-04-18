class WebException(Exception):
    status = b"500 Internal Server Error"


class BadRequestException(WebException):
    status = b"400 Bad Request"


class NotFoundException(WebException):
    status = b"404 Not Found"


class ClientDisconnectException(WebException):
    status = b"499 Client Closed Request"


# TODO standardise extractParams with separator arg - support queryString OR cookies

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


def getSessionCookie(requestMap, cookieName=b"session"):
    cookies = requestMap.get("cookies")
    if cookies is not None:
        cookieValue = cookies.get(cookieName)
        if cookieValue is not None:
            return cookieValue
    return None


def lazyCreateSessionCookie(requestMap, cookieName=b"session"):
    from vgkits.random import randint
    cookies = requestMap.get("cookies")
    if cookies is None:
        cookies = {}
        requestMap["cookies"] = cookies
    cookieValue = cookies.get(cookieName)
    if cookieValue is None:
        cookieValue = str(randint(1000000000)).encode('utf-8')  # todo hardware seeding
        cookies[cookieName] = cookieValue
    return cookieValue


def createReadReceiver(map, debug=False):
    """Factory for a generator consuming HTTP headers line by line via send()
    Generator extracts GET and POST method, path, resource, param and cookie keypairs.
    returns a map of extracted values"""
    while True:
        line = yield None # consider making lowercase before processing
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

    if map["method"] == b"POST":
        if (map["contentLength"] > 0 and
                b"application/x-www-form-urlencoded" in map["contentType"]):
            postBody = yield map["contentLength"] # consume body content for keypairs
            if debug:
                print(postBody)
            map.update(params=extractParams(postBody))
        else:
            raise BadRequestException("POST not x-www-form-urlencoded")

    return map