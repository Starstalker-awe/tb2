from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from dotenv import dotenv_values as load_env
from dotmap import DotMap
import datetime

ENV = DotMap(load_env("../.env"))

HIST_DATA_CLIENT = StockHistoricalDataClient(api_key=ENV.ALPACA_API, secret_key=ENV.ALPACA_SECRET)

TICKER = "AAPL"

data = DotMap(HIST_DATA_CLIENT.get_stock_bars(StockBarsRequest(
    symbol_or_symbols="AAPL",
    start=datetime.datetime(2023, 9, 25, 3 + 12 + 4, 59, 0, tzinfo=datetime.timezone.utc),
    end=datetime.datetime(2023, 9, 25, 4 + 12 + 4, 0, 0, tzinfo=datetime.timezone.utc),
    timeframe=TimeFrame(
        amount=1,
        unit=TimeFrameUnit('Min')
    )
))).data[TICKER][0].close

print(data)