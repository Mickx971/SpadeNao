from Queue import Queue
from community.core import Behaviour


class TaskExecutor(Behaviour):
    def __init__(self):
        super(TaskExecutor, self).__init__("TaskExecutor")
        self.waitingTasks = Queue()

    def onStart(self):
        print "TaskExecutor started"

    def onEnd(self):
        print "TaskExecutor ended"

    def addTask(self, task):
        self.waitingTasks.put(task)

    def _process(self):
        task = self.waitingTasks.get(True)
        task.run()
