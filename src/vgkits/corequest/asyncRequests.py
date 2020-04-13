from vgkits.agnostic import asyncio, socket, select, gc
from vgkits.corequest import createReadReceiver, getSessionCookie, WebException, NotFoundException, BadRequestException


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


async def mapStream(stream, debug=False):
    requestMap = dict()
    readReceiver = createReadReceiver(requestMap, debug)
    await receiveStream(stream, readReceiver)
    return requestMap


async def mapSocketAsync(clientSocket, debug=False):
    return await mapStream(asyncio.StreamReader(clientSocket), debug)


async def completeAsyncRequest(cl, asyncRequestHandler, debug):
    try:
        map = await mapSocketAsync(cl, debug)  # read headers, post body
        if map is None or map == {}:
            raise WebException("Request empty")
        if debug:
            print(map)
        await asyncRequestHandler(cl, map)
    finally:
        cl.shutdown(socket.SHUT_RDWR)
        cl.close()


async def serveAsyncRequests(asyncRequestHandler, port=8080, debug=False,
                             cb=lambda addr, port: print("Serving on {}:{} ".format(addr, port))):
    s = socket.socket()
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
        s.bind(addr)
        s.listen(5)
        cb(addr, port)
        poller = select.poll()
        poller.register(s, select.POLLIN)
        while True:
            gc.collect()  # clear memory
            res = poller.poll(1)  # 1ms block
            if res:  # Only s is polled
                cl, addr = s.accept()  # start handling a request
                requestCompletion = completeAsyncRequest(cl, asyncRequestHandler, debug)
                asyncio.get_event_loop().create_task(requestCompletion)
            # TODO reduce this ( https://github.com/peterhinch/micropython-async/blob/master/client_server/userver.py )
            # TODO see also listen backlog
            await asyncio.sleep_ms(200)
    finally:
        s.close()
