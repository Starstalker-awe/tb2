import helpers
from contextlib import suppress
from dotmap import DotMap
import socketio
import threading
import functools
import datetime
import logging
import asyncio
import math
import os

CPU_THREADS = len(os.sched_getaffinity(0))

logging.basicConfig(format=helpers.settings.LOGGING_FORMAT)
logging.getLogger(__name__).setLevel(helpers.settings.LOGGING_LEVEL)


class Watcher:
	def __init__(self, ticker: str, i: int, trigger: threading.Event, killer: threading.Event, interval = 1):
		self._task = None
		self._starter = trigger
		self._killer = killer

		self.uid = i
		self.ticker = ticker
		self.interval = interval
		self.running = False
		self.chart = helpers.charts.Chart(ticker, date=datetime.datetime.utcnow())

		asyncio.run(self.handler())
		
		return self
		
	async def handler(self):
		self._starter.wait()
		self.start()

		self._killer.wait()
		self.stop()

	def pass_data(self, data: helpers.charts.Datapoint): self.chart.add(data)

	async def start(self):
		if not self.running:
			self.running = True
			self._task = asyncio.ensure_future(self._run())
	async def stop(self):
		if self.running:
			self.running = False
			self._task.cancel()
			with suppress(asyncio.CancelledError): await self._task
	async def _run(self):
		while True:
			await asyncio.sleep(self.interval)
			# Run code here
			

class WatcherList:
	def __init__(self, tickers: list[str], starter: threading.Event, killer: threading.Event):
		self._watchers: list[Watcher] = [None] * len(tickers)
		self._starter: threading.Event = threading.Event()
		self._killers: list[threading.Event] = [threading.Event()] * len(tickers)

		self.starter = starter
		self.killer = killer
		self.tickers = [None] * len(tickers)

		for i, ticker in enumerate(tickers):
			self.tickers[i] = Watcher(ticker, i, self._starter, self._killers[i], interval=1)

		asyncio.run(self.handler())

		return self

	async def handler(self):
		self.starter.wait() # Passed as arg
		self._starter.set() # Private internal trigger

		self.killer.wait()
		for i, ticker in enumerate(self.tickers): self._killers[i].set()

	
class Trader:
	def __init__(self):
		self.state = threading.Event()
		self.stocks = helpers.settings.DB.execute("SELECT * FROM symbol")

		self.ws = socketio.Client()

	def generate(self, threads: list[threading.Thread] = []):
		threads = [None] * (c := math.ceil(len(self.stocks) / CPU_THREADS))
		for i in range(c): threads[i] = threading.Thread(target=WatcherList, args=(self.stocks[i*c:(i+1)*c],self.state,))
		
		self.setup_socket_routes(self.ws)
		self.ws.connect("ws://127.0.0.1:5000", namespaces='/internal')		
		
		for thread in threads: thread.start()

	def setup_socket_routes(socket: socketio.Client):
		def verified(data: object): DotMap({'auth': helpers.settings.ENV.INTERNAL_API_KEY, 'data': data})

		@socket.event
		def connect(): socket.emit("auth", helpers.settings.ENV.INTERNAL_API_KEY)