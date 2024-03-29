from asyncio import sleep, Queue, 
from hx711 import HX711

class Driver:
  def __init__(self) -> None:
      self.hx = HX711(13, 19)
      self.listener = []
      self.hx.set_reading_format("MSB", "MSB")
      self.hx.set_reference_unit(-438)
      self.zero()

  def read(self) -> int:
      self.hx.reset()
      return int(self.hx.get_weight(1))

  def register(self, listener) -> None:
      self.listener.append(listener)

  async def update(self) -> None:
      weight = self.read()
      for listener in self.listener:
        await listener.update(weight)

  def zero(self):
      self.hx.reset()
      self.hx.tare()

class Scale:
  def __init__(self, driver: Driver) -> None:
      self.driver = driver
      self.value = 0

      driver.register(self)
      self.outputs = []
      self.executing = True
  
  def addOutput(self, output):
      self.outputs.append(output)
  
  async def getWeight(self) -> int:
      return self.value

  async def update(self, value: int) -> None:
      # print('Received %s' % value)
      self.value = value
      await sleep(0.5)
      # print(self.buffer)

  async def out(self):
      while self.executing:
        for output in self.outputs:
            await output.print(await self.getWeight())
        await sleep(0.5)

class PrintInterface:
  def __init__(self, socket) -> None:
      self.executing = False
      self.waitFor = 1000
      self.socket = socket
      self.queue = Queue()

  async def print(self, weight):
    print(weight)
    await self.socket.emit('scale', '%d' % weight)

  def cmd(self):
      return self.queue.get()
