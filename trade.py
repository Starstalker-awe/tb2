from yfinance import Ticker, Tickers
from helpers import settings
import threading
import logging
import cs50
import math
import os

logging.basicConfig(format=settings.LOGGING_FORMAT)
logging.getLogger(__name__).setLevel(settings.LOGGING_LEVEL)

CPU_THREADS = len(os.sched_getaffinity(0))
DB = cs50.SQL("sqlite:///data.db")

class Watcher:
    def __init__(self, ticker: str, trigger: threading.Event):
        self.ticker = Ticker(ticker)

        trigger.wait()

class WatcherList:
    def __init__(self, tickers: list, trigger: threading.Event):
        self.trigger = threading.Event()
        self.tickers = [Watcher(t, self.trigger) for t in tickers]
        
        trigger.wait()

        self.trigger.set()

class Trader:
    def __init__(self, threads: list[threading.Thread] = [], stocks: list[str] = []):
        self.run = threading.Event()

        stocks = list(map(lambda s:s[1], DB.execute("SELECT * FROM symbol")))
        logging.info(f"\tBeginning setup of watcher threads")

        threads = [None] * (c := math.ceil(len(stocks) / CPU_THREADS))
        for i in range(c):
            threads[i] = threading.Thread(target=WatcherList, args=(stocks[i*c:(i+1)*c],self.run,))