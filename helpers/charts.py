from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.requests import StockBarsRequest

import threading
import datetime
import settings
import pause
import asyncio

CLIENT = StockHistoricalDataClient(api_key=settings.SECRETS["ALPACA_API"], secret_key=settings.SECRETS["ALPACA_SECRET"])

class Datapoint:
    def __init__(self, timestamp: datetime.datetime, ask_price: float, bid_price: float, **extra):
        self.timestamp = timestamp
        self.ap = ask_price
        self.bp = bid_price

        return self

class Bar:
    def __init__(self, timestamp: datetime.datetime):
        self.closed = False
        # Placeholders to be used in functions
        self._high, self._low, self._open, self._close = [None] * 4

        return self

    def close(self, high = None, low = None, open = None, close = None): # Clear datapoints when minute has passed
        self._high = high or self.high()
        self._low = low or self.low()
        self._open = open or self.open()
        self._close = close or self.close()
        # Use values before clearing data
        self.datapoints = []
        self.closed = True

        return self
    def add(self, data: Datapoint): self.datapoints.append(data)

    def high(self): self._high or max(list(map(lambda d:d.bp, self.datapoints)))
    def low(self): self._low or min(list(map(lambda d:d.ap, self.datapoints)))
    def open(self): self._open or self.datapoints[0].bp
    def close(self): self._close or self.datapoints[-1].bp

class Chart:
    def __init__(self, ticker: str, date: datetime.datetime):
        self.bars: [Bar] = []
        self.ticker = ticker
        self.today = [date.year, date.month, date.day]
        self.caught_up = threading.Event()

        self._MARKET_OPEN = datetime.datetime(*self.today, hour=13, minutes=30, tzinfo=datetime.timezone.utc)

        if datetime.datetime.utcnow().replace(second=0, microsecond=0) != self._MARKET_OPEN:
            asyncio.run(self.fill_bars(datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(minutes=1)))
        else: self.caught_up.set()

        for i in range(7):
            for i2 in range(60):
                if len(self.bars) < 390: # Total number of minutes in a trading day
                    self.bars.append(Bar(datetime.datetime(
                        *self.today, # Add year month and day without spending sanity
                        hour=(9 + 4 + i), # Starts at 9:30 (accounted for) and is GMT-4
                        minute=(i2 + 30 if i == 0 else i2), # If hour 0 (9:__) add 30 minutes
                        tzinfo=datetime.timezone.utc # Keep everything in UTC to stay sane!
                    )))

        return self

    def add(self, data: Datapoint):
        time = data.timestamp - datetime.timedelta(hours=(9 + 4))
        self.bars[index := (time.hours * 60 + time.minutes)].add(data)
        if index > 0: 
            if not self.bars[index - 1].closed: self.bars[index - 1].close()

        return self

    async def fill_bars(self, wait_til: datetime.datetime):
        await pause.until(wait_til + datetime.timdeelta(minutes=15))
        data = CLIENT.get_stock_bars(StockBarsRequest(
                self.ticker,
                start=self._MARKET_OPEN + datetime.timedelta(minutes=1),
                end=datetime.datetime.utcnow(),
                timeframe=TimeFrame(
                    amount_value=1,
                    unit=TimeFrameUnit("Min")
                )
            ))
        for (i, bar) in enumerate(data.data[self.ticker]):
            self.bars[i] = Bar(timestamp=bar.timestamp).close(**bar)

        self.caught_up.set()

    def high(self): max(list(map(lambda d:d.high(), self.bars)))
    def low(self): min(list(map(lambda d:d.low(), self.bars)))
    def open(self): self.bars[0].open()
    def close(self): self.bars[-1].close()
    def current(self): self.close()