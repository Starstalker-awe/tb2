from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.requests import StockBarsRequest

from dotmap import DotMap
import multiprocessing
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
	def __init__(self, ticker: str, i: int, trigger: threading.Event, killer: threading.Event, Wlist, interval = 1):
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

		Wlist[i] = self

		if not self.chart.caught_up.is_set():
			logging.debug(f'\t\tWatcher {self.uid}: Waiting to catch up with chart')
			self.chart.caught_up.wait()
			logging.debug(f'\t\tWatcher {self.uid}: Chart caught up!')

		trigger.wait()

		if datetime.datetime.utcnow() < datetime.datetime(*self.today, 9 + 4, 30, 1): 
			threading.Thread(target=self.gap_check, args=[self.yesterday]).start()

		threading.Thread(target=self.stoppable(self.buy_rules), args=[self.starter, killer]).start()
		threading.Thread(target=self.stoppable(self.sell_rules), args=[self.starter, killer]).start()
		threading.Thread(target=self.starter_f).start()


	def gap_check(self, yesterday: list[int]):
		logging.debug(f'\t\tWatcher {self.uid}: Starting gap checker')
		yclose = DotMap(helpers.settings.HIST_DATA_CLIENT.get_stock_bars(StockBarsRequest(
			symbol_or_symbols=self.ticker,
			start=datetime.datetime(*yesterday, 3 + 12 + 4, 59, 0, tzinfo=datetime.timezone.utc),
			end=datetime.datetime(*yesterday, 4 + 12 + 4, 0, 0, tzinof=datetime.timezone.utc),
			timeframe=TimeFrame(amount=1, unit=TimeFrameUnit('Min'))
		))).data[self.ticker][0].close

		if self.chart.current() == yclose: return
		elif self.chart.current() > yclose:
			pass # Short order at self.chart.bars[0].open() - .01
		else:
			pass # Short order at market


	def buy_rules(self):
		logging.debug(f'\t\tWatcher {self.uid}: Starting buy rules runner')
		while True:
			# Code here
			time.sleep(self.interval)

	def sell_rules(self):
		logging.debug(f'\t\tWatcher {self.uid}: Starting sell rules runner')
		while True:
			# Code here
			time.sleep(self.interval)

	def starter_f(self):
		time.sleep(26 * 60)
		self.starter.set()


	def pass_data(self, data: helpers.charts.Datapoint): self.chart.add(data)




class WatcherList:
	def __init__(self, tickers: list[str], starter: threading.Event, killers: list[threading.Event], WLlist, id: int):
		
		self._threads: list[threading.Thread] = [threading.Thread] * len(tickers)
		self.watchers: list[Watcher] = list[Watcher] * len(tickers)

		for i, ticker in enumerate(tickers):
			self._threads[i] = threading.Thread(
				target=Watcher, 
				args=[
					ticker, 
					i, 
					starter, 
					killers[ticker],
					self.watchers
				]
			)
			self._threads[i].start()

		WLlist[id] = self

	def tickers(self): list(map(lambda t:t.ticker, self._threads))




class Trader:
	def __init__(self):
		self.state = threading.Event()
		self.stocks = list(map(lambda i:i['symbol'], helpers.settings.DB.execute("SELECT * FROM symbol")))
		self.killers = {tick: threading.Event() for tick in self.stocks}

		self.ws = socketio.Client()

	def generate(self):
		self._threads = [multiprocessing.Process] * (c := math.ceil(len(self.stocks) / CPU_THREADS))
		self.watcherlists: list[WatcherList] = [WatcherList] * c
		
		for i in range(c):
			self._threads[i] = multiprocessing.Process(
				target=WatcherList, 
				args=[
					self.stocks[i*c:(i+1)*c], 
					self.state, 
					self.killers, 
					self.watcherlists, 
					i
				]
			)

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


	def kill_watcher(self, ticker: str):
		k = self.killers.get(ticker)
		if k:
			k.set()
			del self.killers[ticker]