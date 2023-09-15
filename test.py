from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.requests import StockBarsRequest
from helpers import settings
import datetime

CLIENT = StockHistoricalDataClient(api_key=settings.SECRETS["ALPACA_API"], secret_key=settings.SECRETS["ALPACA_SECRET"])

data = \
    CLIENT.get_stock_bars(
        StockBarsRequest(
            symbol_or_symbols="AAPL",
            start=datetime.datetime(2023, 9, 15, 13, 30, tzinfo=datetime.timezone.utc),
            end=datetime.datetime(2023, 9, 15, 17, 46, tzinfo=datetime.timezone.utc),
            timeframe=TimeFrame(
                amount=1,
                unit=TimeFrameUnit("Min")
            )
        )
    )

print((data.data['AAPL'])[0:3])