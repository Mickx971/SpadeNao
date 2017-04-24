import sys
from community.core import PeriodicBehaviour


class MainBehaviour(PeriodicBehaviour):
    def __init__(self):
        super(MainBehaviour, self).__init__("MainBehaviour", 1)
        self.tick = 0

    def _onTick(self):
        self.tick = self.tick + 1
        try:
            print self.tick
            print self.myAgent.askBelieve("bonjour(X)")
        except:
            print "Ex1"
            print "Unexpected error:", sys.exc_info()[0]

