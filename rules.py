bars, this, previous_red, previous_green, shares, get = None
def yesterday():return 0
def buy():return 0
def sell():return 0

# == BUY RULES ==
if bars[0].current > yesterday(this).close: # Gaps up
    if bars[0].current > bars[0].open: # Above open
        buy(200)
else: # Gaps down
    if len(bars) == 1: # First bar
        if bars[0].price > bars[0].open and get("SPY").current > get("SPY").open: # If goes above open in first bar
            buy(200)
    elif get(this).current > bars[0].open: # Goes above open at any time
        buy(200)

# Moving upwards, above previous red
if (bars[-3].close > previous_red.percent(60) or bars[-2].close > previous_red.percent(60)) and bars[-1].current > bars[-1].open:
    buy(200 if not shares(this) else 100)

if shares(this) > 0:
    if get(this).current > bars[-2].close:
        buy(100)
# == BUY RULES ==

# == SELL RULES ==
if get(this).current < previous_green.percent(40):
    sell(sold_drop := (shares(this) / 2)); sold_at_40 = True
if sold_at_40 and get(this).current > previous_green.percent(40):
    buy(sold_drop)

if get(this).current < previous_green.low:
    sell()
# == SELL RULES ==