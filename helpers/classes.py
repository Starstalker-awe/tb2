import multiprocessing

class Stoppable:
	def __init__(self):
		self.tasks: list[multiprocessing.Process] = []

	def stoppable(self, strtr, stpr, f, *a, **ka):
		self.tasks.append(multiprocessing.Process(target=f, args=a, kwargs=ka))
		id = len(self.tasks) - 1

		strtr.wait()
		self.tasks[id].start()

		stpr.wait()
		self.tasks[id].terminate()