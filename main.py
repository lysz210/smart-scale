import aiohttp
from aiohttp import web
from socketio import AsyncServer

import asyncio

from smart_scale.scale import *


d = Driver()
s = Scale(d)

async def update():
  while True:
    await d.update()

app = web.Application()
sio = AsyncServer()
sio.attach(app)
p = PrintInterface(sio)
s.addOutput(p)

@sio.event
def connect(sid, environ):
    print('connect ', sid)
@sio.event
async def chat_message(sid, data):
    print('message ', data)

routes = web.RouteTableDef()

@routes.get('/')
async def index(request):
    return web.FileResponse('./templates/index.html')

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