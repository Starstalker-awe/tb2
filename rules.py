bars, this, previous_red, previous_green, shares, i = None
def yesterday(): get().close
def buy(shares: int, lvl: int = None): shares, lvl
def sell(shares: int, lvl: int = None): shares, lvl
def cancel(): None
def get(ticker: str): ticker
def wait(time: int): time
def kill_branch(): None


class if_gap_up:
    def running():
        wait(60)
        if bars[i].current > bars[0].open:
            sell(shares, bars[0].open - 0.01)
            kill_branch()
        else: # Went below, within 10s
            sell(shares, bars[i].current)
            kill_branch()

    def side():
        wait(13 * 60) # after 13 minutes
        cancel()
        kill_branch()


class if_gap_down:
    def running():
        wait(10)
        if bars[0].current < yesterday().close: # Still down
            if bars[i].current < bars[0].open:
                buy(shares, bars[0].open + 0.01)
                kill_branch()
        else: # Went above, within 10s
            buy(shares, bars[i].current)
            kill_branch()

    def side():
        wait(13 * 60) # after 13 minutes
        cancel()
        kill_branch()


class normal:
    def running(minutes = 13):
        if (bars[i - 2].close > previous_red.percent(60) or bars[i - 1].close > previous_red.percent(60)) and bars[i].current > bars[i].open:
            # if big red, then green > 60%, then red close < 60%: wait 'til red open
            buy(200 if shares == 0 else 100)













# == BUY RULES ==

# Moving upwards, above previous red

if shares > 0:
    if bars[i].current > bars[i - 1].close:
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