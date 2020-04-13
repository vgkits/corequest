from vgkits.agnostic import socket, gc

from vgkits.corequest import createReadReceiver, getSessionCookie, WebException, NotFoundException, BadRequestException


def receiveFile(file, readReceiver):
    """Blocking sync equivalent of async#receiveStream"""
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


def mapSocketSync(clientSocket, debug=False):
    """Makes blocking reads of the clientSocket, decoding bytes
    as lines of a HTTP request. Returns a map describing the request.
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

def completeSyncRequest(cl, syncRequestHandler, debug):
    try:
        map = mapSocketSync(cl, debug)  # read headers, post body
        if map is None or map == {}:
            raise WebException("Request empty")
        if debug:
            print(map)
        syncRequestHandler(cl, map)  # pass to request handler
    finally:
        cl.shutdown(socket.SHUT_RDWR)
        cl.close()


def serveSyncRequests(syncRequestHandler, port=8080, debug=False,
                      cb=lambda addr, port: print("Serving on {}:{} ".format(addr, port))):

    s = socket.socket()
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
        s.bind(addr)
        s.listen(5)
        cb(addr, port)

        while True:
            gc.collect()  # clear memory
            cl, addr = s.accept()  # start handling a request
            completeSyncRequest(cl, syncRequestHandler, debug)
    finally:
        s.close()
