from vgkits.corequest import createReadReceiver


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
