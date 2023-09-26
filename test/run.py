import threading
import classes_def
import asyncio

class Parent(classes_def.S1Loop):
    def __init__(self, ticker: str, starter: threading.Event, killer: threading.Event):
        super()

        self.ticker = ticker

    async def start(self):
        s2 = threading.Event()
        super(self.start(
            lambda: self.gap_check(s2)
        ))
    
    async def _run(self):
        print("Running from _run")



    class gap_check(classes_def.S1Loop):
        def __init__(self, starter: threading.Event, killer = threading.Event()):
            super(starter, killer)

            self.killer = killer

        async def start(self):
            super(self.start(
                lambda: self.timeout()
            ))
        async def _run(self):
            print("Running from gap_check._run")
        async def timeout(self):
            asyncio.sleep(15)
            self.killer.set()



if __name__ == '__main__':
    gstart = threading.Event()
    gkill = threading.Event()

    prnt = Parent('boo', gstart, gkill)