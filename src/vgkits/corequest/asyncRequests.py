from vgkits.agnostic import asyncio
from vgkits.corequest import createReadReceiver

async def receiveStream(stream, readReceiver):
    """Async/await equivalent of sync#receiveFile"""
    try:
        count = readReceiver.send(None)  # run to first yield
        while True:
            if count is None:
                count = readReceiver.send((await stream.readline()))
            else:
                count = readReceiver.send((await stream.read(count)))
    except StopIteration:
        pass


async def mapReader(reader, debug=False):
    requestMap = dict()
    readReceiver = createReadReceiver(requestMap, debug)
    await receiveStream(reader, readReceiver)
    return requestMap


async def serveAsyncRequests(asyncRequestHandler, port=8080, debug=False):
    async def clientConnected(reader, writer):
        try:
            map = await mapReader(reader, debug)
            if debug:
                print(map)
            await asyncRequestHandler(writer, map)
            await writer.drain()
        finally:
            writer.close()

    await asyncio.start_server(clientConnected, port=port, reuse_address=True)