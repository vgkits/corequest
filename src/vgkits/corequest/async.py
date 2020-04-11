from vgkits.corequest import createReadReceiver


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
