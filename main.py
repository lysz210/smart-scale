import aiohttp
from aiohttp import web

import asyncio

from smart_scale.scale import *


d = Driver()
s = Scale(d)

async def update():
  while True:
    await d.update()

app = web.Application()

routes = web.RouteTableDef()

@routes.get('/')
async def index(request):
    return web.FileResponse('./templates/index.html')
@routes.get('/ws')
async def ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    p = PrintInterface(ws)
    s.addOutput(p)
    async for msg in ws:
        print(msg)
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str(msg.data + '/answer')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())
    return ws

app.add_routes(routes)

async def run(application):
    runner = web.AppRunner(application)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

loop = asyncio.new_event_loop()
loop.create_task(run(app))
loop.create_task(s.out())
loop.create_task(update())
loop.run_forever()