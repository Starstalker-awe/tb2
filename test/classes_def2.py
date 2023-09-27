import multiprocessing
import threading
import time

class Stoppable:
	def __init__(self):
		self.tasks: list[multiprocessing.Process] = []

	def stoppable(self, func):
		def __handler(strtr: threading.Event, stpr: threading.Event, *a, **ka):
			self.tasks.append(multiprocessing.Process(target=func))
			id = len(self.tasks) - 1

			strtr.wait()
			self.tasks[id].start()

			stpr.wait()
			self.tasks[id].terminate()

		return __handler


class Test(Stoppable):
	def __init__(self, starter: threading.Event, stopper: threading.Event):
		Stoppable.__init__(self)
		threading.Thread(target=self.stoppable(self.run), args=[starter, stopper]).start()
		threading.Thread(target=self.stoppable(self.run2), args=[starter, stopper]).start()
		threading.Thread(target=self.timeout, args=[stopper]).start()

	def run(self):
		while True:
			print(123)
			time.sleep(1)

	def run2(self):
		while True:
			print(456)
			time.sleep(1)

	def timeout(self, stopper: threading.Event):
		time.sleep(2 + (len(self.tasks) * 0.01))
		stopper.set()
		print("Stopper set")


strtr = threading.Event()
stpr = threading.Event()

targ = threading.Thread(target=Test, args=[strtr, stpr])
targ.start()

time.sleep(1)
print("re-sync attempt")

strtr.set()
#targ.terminate()