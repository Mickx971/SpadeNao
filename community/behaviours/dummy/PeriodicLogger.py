import sys
from community.core import PeriodicBehaviour
from time import sleep

class MainBehaviour(PeriodicBehaviour):
    def __init__(self):
        super(MainBehaviour, self).__init__("MainBehaviour", 1)
        self.tick = 0

    def _onTick(self):
        self.tick = self.tick + 1
        try:
            print self.tick
            print self.myAgent.askBelieve("bonjour(X)")
            if self.tick == 1:
                self.myAgent.addBelieve("bonjour(mickael)")
        except Exception as e:
            print "MainBehaviour:"
            print "Unexpected error:", type(e)
            print e

