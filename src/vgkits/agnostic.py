import sys

isMicropython = sys.implementation.name == "micropython"

if isMicropython:
    import uasyncio as asyncio
    sleep_ms = asyncio.sleep_ms
    import usocket as socket
    import uselect as select
    import gc
else:
    import asyncio
    async def sleep_ms(ms):
        await asyncio.sleep(ms * 0.001)
    import socket
    import select
    def noop():
        pass
    class AttrObj:
        pass
    gc = AttrObj()
    setattr(gc, "collect", noop)
