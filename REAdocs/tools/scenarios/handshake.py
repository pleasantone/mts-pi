# Standard setup, then idle long enough to see two PING/PONG rounds and the held incremental request.
async def scenario(d):
    await d.setup()
    await d.sleep(4.5)
