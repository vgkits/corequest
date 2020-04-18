from vgkits.agnostic import asyncio, isMicropython
from vgkits.corequest import createReadReceiver, WebException, ClientDisconnectException

async def receiveStream(stream, readReceiver):
    """Async/await equivalent of sync#receiveFile"""
    # TODO add logic aligned with receiveFile -
    try:
        count = readReceiver.send(None)  # run to first yield
        while True:
            if count is None:
                data = await stream.readline()
            else:
                data = await stream.read(count)
            if data:
                count = readReceiver.send(data)
                continue
            else:
                raise ClientDisconnectException
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
            # await writer.drain()
        except WebException as we:
            if isinstance(we, ClientDisconnectException):
                print("0 bytes received. Stale preconnect?")
            else:
                print("{} : ".format(we))
        finally:
            if isMicropython:
                await writer.aclose() # this await was required, although not in python3
            else:
                writer.close() # note, not awaited (wait_closed available since 3.7)

    if isMicropython:
        await asyncio.start_server(clientConnected, "0.0.0.0", port, backlog=5)
    else:
        await asyncio.start_server(clientConnected, "0.0.0.0", port, backlog=5, reuse_address=True)
