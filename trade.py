from contextlib import suppress
from dotmap import DotMap
import socketio
import threading
import datetime
import helpers
import logging
import asyncio
import math
import os

CPU_THREADS = len(os.sched_getaffinity(0))

logging.basicConfig(format=helpers.settings.LOGGING_FORMAT)
logging.getLogger(__name__).setLevel(helpers.settings.LOGGING_LEVEL)


class Watcher(helpers.classes.Stoppable):
	def __init__(self, ticker: str, i: int, trigger: threading.Event, killer: threading.Event, interval = 1):
		helpers.classes.Stoppable.__init__(self)

		self.uid = i
		self.ticker = ticker
		self.interval = interval
		self.chart = helpers.charts.Chart(ticker, date=datetime.datetime.utcnow())

		self.chart.caught_up.wait()

	def pass_data(self, data: helpers.charts.Datapoint): self.chart.add(data)

	class GapCheck(helpers.classes.Stoppable):
		def __init__(self):
			helpers.classes.Stoppable.__init__(self)


class WatcherList:
	def __init__(self, tickers: list[str], starter: threading.Event, killers):
		self.watchers = list[Watcher] = [None] * len(tickers)

		for i, ticker in enumerate(tickers):
			self.watchers[i] = Watcher(ticker, i, starter, killers[ticker])

	def tickers(self): list(map(lambda t:t.ticker, self.watchers))


class Trader:
	def __init__(self):
		self.state = threading.Event()
		self.stocks = list(map(lambda i:i['symbol'], helpers.settings.DB.execute("SELECT * FROM symbol")))
		self.killers = {tick: threading.Event() for tick in self.stocks}

		self.ws = socketio.Client()

	def generate(self):
		self._threads = [None] * (c := math.ceil(len(self.stocks) / CPU_THREADS))
		for i in range(c): self._threads[i] = threading.Thread(target=WatcherList, args=(self.stocks[i*c:(i+1)*c],self.state,))

		self.setup_socket_routes(self.ws)
		self.ws.connect("ws://127.0.0.1:5000", namespaces='/internal')

		for thread in self._threads: thread.start()

	def setup_socket_routes(self, socket: socketio.Client):
		def verified(data: object): DotMap({'auth': helpers.settings.ENV.INTERNAL_API_KEY, 'data': data})

		@socket.event
		def connect(): socket.emit("auth", helpers.settings.ENV.INTERNAL_API_KEY)

		@socket.event
		def new_ticker(ticker: str):
			self.stocks.append(ticker)
			self.killers[ticker] = threading.Event()


	def kill_watcher(ticker: str):
		pass