import sys
if sys.implementation.name == "micropython":
    import uasyncio as asyncio
else:
    import asyncio