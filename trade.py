from helpers import settings
import threading
import logging
import time
import cs50
import math
import os

logging.basicConfig(format=settings.LOGGING_FORMAT)
logging.getLogger(__name__).setLevel(settings.LOGGING_LEVEL)


class Watcher:
	def __init__(self, ticker: str, i: int, trigger: threading.Event):
		pass

	def add_data(self):
		pass

class WatcherList:
	def __init__(self, tickers: list[str], trigger: threading.Event):
		self._watchers: list[Watcher] = [None] * len(tickers)
		self._trigger: threading.Event = threading.Event()
		self._tickers = [None] * len(tickers)

		for i, ticker in enumerate(tickers):
			self._tickers[i] = Watcher(ticker, i, self._trigger)

		trigger.wait()
		self._trigger.set()

	def getTicks(self): return self._tickers


class Trader:
	def __init__(self, stocks: list[str] = [], threads: list[threading.Thread] = []):
		self.run = threading.Event()

		stocks = [*list(map(lambda s:s[1], settings.DB.execute("SELECT * FROM symbol"))), *stocks]
		logging.info(f"\tBeginning setup of watcher threads")

		threads = [None] * (c := math.ceil(len(stocks) / settings.CPU_THREADS))
		for i in range(c):
			threads[i] = threading.Thread(target=WatcherList, args=(stocks[i*c:(i+1)*c],self.run,))