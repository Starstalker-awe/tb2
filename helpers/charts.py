from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.requests import StockBarsRequest

from dotmap import DotMap
from . import settings
import threading
import datetime
import asyncio
import pause
import math

class Datapoint:
    def __init__(self, timestamp: datetime.datetime, ask_price: float, bid_price: float, **extra):
        self.timestamp = timestamp
        self.ap = ask_price
        self.bp = bid_price

class Bar:
    def __init__(self, timestamp: datetime.datetime):
        self.closed = False
        self.timestamp = timestamp
        self._high, self._low, self._open, self._close = [None] * 4

    def close(self, high = None, low = None, open = None, close = None): # Clear datapoints when minute has passed
        self._high = high or self.high()
        self._low = low or self.low()
        self._open = open or self.open()
        self._close = close or self.close()
        # Use values before clearing data
        self.datapoints = []
        self.closed = True

        return self

    def add(self, data: Datapoint): self.datapoints.append(data) if not self.closed else None

    def percent(self, lvl: int): self.low() + ((self.high() - self.low()) * (100 / lvl))

    def change(self): abs((self.close() - self.open()) if self.close() > self.open() else (self.open() - self.close()))

    def high(self): self._high or max(list(map(lambda d:d.bp, self.datapoints)))
    def low(self): self._low or min(list(map(lambda d:d.ap, self.datapoints)))
    def open(self): self._open or self.datapoints[0].bp
    def close(self): self._close or self.datapoints[-1].bp
    def data(self): DotMap({'high': self.high(), 'low': self.low(), 'open': self.open(), 'close': self.close()})

class Chart:
    def __init__(self, ticker: str, date: datetime.datetime):
        self.bars: list[Bar] = []
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

    def add(self, data: list[Datapoint | Bar], type: Datapoint | Bar = Datapoint):
        for point in data:
            time = point.timestamp - datetime.timedelta(hours=(9 + 4))
            i = (time.hours * 60) + time.minutes
            if type is Datapoint:
                self.bars[i].add(point)
            elif type is Bar:
                self.bars[i] = point
            if i > 0: 
                if not self.bars[i - 1].closed: self.bars[i - 1].close()

        return self
    
    def group(self, length: int):
        for group in range(math.ceil(len(self.bars) / length)):
            tg = self.bars[length*group:length*(group+1)]
            tg = list(map(lambda t:t.data(), tg))
            
            high = max(list(map(lambda t:t.high, tg)))
            low = min(list(map(lambda t:t.low, tg)))

            return DotMap({'high': high, 'low': low, 'open': tg[0].open, 'close': tg[-1].close})

    def previous_green(self, count = 1):
        for i in range(len(self.bars), 0, -1):
            if self.bars[i].close() > self.bars[i].open():
                count = count - 1
                if count == 0:
                    return self.bars[i]

    def previous_red(self, count = 1):
        for i in range(len(self.bars), 0, -1):
            if self.bars[i].close() < self.bars[i].open():
                count = count - 1
                if count == 0:
                    return self.bars[i]

    async def fill_bars(self, wait_til: datetime.datetime):
        await pause.until(wait_til + datetime.timdeelta(minutes=15))
        data = settings.HIST_DATA_CLIENT.get_stock_bars(StockBarsRequest(
                self.ticker,
                start=self._MARKET_OPEN + datetime.timedelta(minutes=1),
                end=datetime.datetime.utcnow(),
                timeframe=TimeFrame(
                    amount_value=1,
                    unit=TimeFrameUnit("Min")
                )
            ))
        for i, bar in enumerate(data.data[self.ticker]):
            self.bars[i] = Bar(timestamp=bar.timestamp).close(**bar)

        self.caught_up.set()

    def high(self): max(list(map(lambda d:d.high(), self.bars)))
    def low(self): min(list(map(lambda d:d.low(), self.bars)))
    def open(self): self.bars[0].open()
    def close(self): self.bars[-1].close()
    def current(self): self.close()