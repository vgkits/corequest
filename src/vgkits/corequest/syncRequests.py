from vgkits.agnostic import socket, gc
from vgkits.corequest import createReadReceiver, getSessionCookie, WebException, NotFoundException, BadRequestException, \
    ClientDisconnectException


def receiveFile(file, readReceiver):
    """Blocking sync equivalent of async#receiveStream"""
    try:
        count = readReceiver.send(None)  # run to first yield
        while True:
            if count is None:
                data = file.readline()
            else:
                data = file.read(count)
            if data:
                count = readReceiver.send(data)
                continue
            else:
                raise ClientDisconnectException
    except StopIteration:
        pass


def mapFile(file, debug=False):
    requestMap = dict()
    readReceiver = createReadReceiver(requestMap, debug)
    receiveFile(file, readReceiver)
    return requestMap


def closeSocketFile(socketFile):
    import sys
    if hasattr(sys, 'implementation'):  # mpy or py3
        name = sys.implementation.name
        if name == "micropython" or name == "circuitpython":
            pass  # s.makefile() was a no-op, closing file will close socket
        else:
            socketFile.close()  # file created above should be closed


def mapSocketSync(clientSocket, debug=False):
    """Makes blocking reads of the clientSocket, decoding bytes
    as lines of a HTTP request. Returns a map describing the request.
    """
    clientFile = clientSocket.makefile('rb', 0)
    try:
        return mapFile(clientFile, debug)
    finally:
        closeSocketFile(clientFile)


def completeSyncRequest(cl, syncRequestHandler, debug):
    try:
        map = mapSocketSync(cl, debug)  # read headers, post body
        if debug:
            print(map)
        clFile = cl.makefile('wb')
        try:
            syncRequestHandler(clFile, map)  # pass to request handler
        finally:
            closeSocketFile(clFile)
    finally:
        cl.shutdown(socket.SHUT_RDWR)
        cl.close()


def serveSyncRequests(syncRequestHandler, port=8080, debug=False,
                      cb=lambda addr, port: print("Serving on {}:{} ".format(addr, port))):
    s = socket.socket()
    s.settimeout(None)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
        s.bind(addr)
        s.listen(5)
        cb(addr, port)

        while True:
            gc.collect()  # clear memory
            cl, addr = s.accept()  # start handling a request
            try:
                completeSyncRequest(cl, syncRequestHandler, debug)
            except WebException as we:
                if isinstance(we, ClientDisconnectException):
                    print("0 bytes received. Stale preconnect?")
                else:
                    print("{} : ".format(we))

    finally:
        s.close()
