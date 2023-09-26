from contextlib import suppress
import threading
import asyncio

class S1Loop:
	def __init__(self, starter: threading.Event, killer: threading.Event):
		self.starter = starter
		self.killer = killer

		self.running = False
		self._task = None

		print(True)

		threading.Thread(target=self.handler).start()

		print("About to return")

		return self
	
	async def handler(self):
		print("Gonna wait now")
		await self.starter.wait()
		self.start()


		await self.killer.wait()
		self.stop()

	async def start(self, extras):
		if not self.running:
			self.running = True
			self._task = asyncio.ensure_future(self._run())
			extras()

	async def stop(self):
		if self.running:
			self.running = False
			self._task.cancel()
			with suppress(asyncio.CancelledError): await self._task

	async def _run(self, func):
		while True:
			await asyncio.sleep(1)
			print("\tRunning _run")
			func()


def main():
	strtr = threading.Event()
	stpr = threading.Event()

	loop = S1Loop(strtr, stpr)

	strtr.set()

	for i in range(60):
		asyncio.sleep(1)
		print(i)

	stpr.set()

if __name__ == '__main__': main()