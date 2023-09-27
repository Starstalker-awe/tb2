from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.requests import StockBarsRequest

from dotmap import DotMap
import socketio
import threading
import datetime
import helpers
import logging
import math
import time
import os

CPU_THREADS = len(os.sched_getaffinity(0))

logging.basicConfig(format=helpers.settings.LOGGING_FORMAT)
logging.getLogger(__name__).setLevel(helpers.settings.LOGGING_LEVEL)


class Watcher(helpers.classes.Subprocess):
	def __init__(self, ticker: str, i: int, trigger: threading.Event, killer: threading.Event, interval = 1):
		helpers.classes.Subprocess.__init__(self)

		self.today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
		self.yesterday = self.today - datetime.timedelta(days=1)

		self.today = [self.today.year, self.today.month, self.today.day]
		self.yesterday = [self.yesterday.year, self.yesterday.month, self.yesterday.day]

		self.uid = i
		self.ticker = ticker
		self.interval = interval
		self.chart = helpers.charts.Chart(ticker, date=datetime.datetime.utcnow())

		self.starter = threading.Event()
		self.stopper = threading.Event()

		if not self.chart.caught_up.is_set():
			logging.debug(f'\t\tWatcher {self.uid}: Waiting to catch up with chart')
			self.chart.caught_up.wait()
			logging.debug(f'\t\tWatcher {self.uid}: Chart caught up!')

		trigger.wait()

		if datetime.datetime.utcnow() < datetime.datetime(*self.today, 9 + 4, 30, 1): 
			logging.debug(f'\t\tWatcher {self.uid}: Starting gap checker')
			self.GapCheck(self.chart, self.yesterday, self.starter)

		


	def run(self):
		while True:
			# Code here
			time.sleep(1)

	def starter_f(self):
		time.sleep(26 * 60)
		self.starter.set()


	def pass_data(self, data: helpers.charts.Datapoint): self.chart.add(data)

	class GapCheck(helpers.classes.Subprocess):
		def __init__(self, chart: helpers.charts.Chart, yesterday: datetime.datetime, pstart: threading.Event):
			helpers.classes.Subprocess.__init__(self)

			self.starter = threading.Event()
			self.stopper = threading.Event()

			self.chart = chart
			self.yesterday = yesterday
			self.direction = chart.open() > (yclose := DotMap(helpers.settings.HIST_DATA_CLIENT.get_stock_bars(StockBarsRequest(
				symbol_or_symbols=self.ticker,
				start=datetime.datetime(*yesterday, 3 + 12 + 4, 59, 0, tzinfo=datetime.timezone.utc),
				end=datetime.datetime(*yesterday, 4 + 12 + 4, 0, 0, tzinof=datetime.timezone.utc),
				timeframe=TimeFrame(amount=1, unit=TimeFrameUnit('Min'))
			))).data[self.ticker][0].close)

			self.starter.wait() # Global starter

			threading.Thread(target=self.stoppable(self.run), args=[self.starter, self.stopper]).start()
			threading.Thread(target=self.starter_f).start()
			threading.Thread(target=self.timeout).start()

		def run(self): # Runs 1 minute after open
			while True:
				if self.direction: # Gapped up
					pass
				else: # Gapped down
					pass
				time.sleep(1)

		def timeout(self):
			time.sleep(13 * 60)
			self.stopper.set()

		def starter_f(self):
			time.sleep(60)
			self.starter.set()


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