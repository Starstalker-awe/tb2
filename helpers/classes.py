import multiprocessing

class Subprocess:
	def __init__(self):
		self.tasks: list[multiprocessing.Process] = []

	def stoppable(self, f):
		def __handler(strtr, stpr, *a, **ka):
			self.tasks.append(multiprocessing.Process(target=f, args=a, kwargs=ka))
			id = len(self.tasks) - 1

			strtr.wait()
			self.tasks[id].start()

			stpr.wait()
			self.tasks[id].terminate()

		return __handler