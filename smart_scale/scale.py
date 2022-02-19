from asyncio import Lock, gather, sleep, run
from array import array
class Driver:
  def __init__(self) -> None:
      self.listener = []
      self.i = 1

  def read(self) -> int:
      retVal = self.i
      self.i += 1
      return retVal

  def register(self, listener) -> None:
      self.listener.append(listener)

  async def update(self) -> None:
      for listener in self.listener:
        await listener.update(self.read())

class Scale:
  def __init__(self, driver: Driver) -> None:
      self.driver = driver
      self.lock = Lock()
      self.buffer = array('i', [0, 0, 0, 0, 0])

      driver.register(self)
  
  async def getWeight(self) -> int:
      async with self.lock:
        return self.buffer[0]

  async def update(self, value: int) -> None:
      # print('Received %s' % value)
      async with self.lock:
        self.buffer.pop(0)
        self.buffer.append(value)
        await sleep(1)
        # print(self.buffer)

import asyncio
class PrintInterface:
  def __init__(self, scale: Scale) -> None:
      self.scale = scale
      self.executing = False
      self.waitFor = 1000

  async def print(self):
      while self.executing:
        print(await self.scale.getWeight())
        await asyncio.sleep(1)

  async def run(self):
      self.executing = True
      await self.print()

d = Driver()
s = Scale(d)
p = PrintInterface(s)

async def update():
  while True:
    await d.update()


loop = asyncio.new_event_loop()
loop.create_task(p.run())
loop.create_task(update())
loop.run_forever()