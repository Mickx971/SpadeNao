from community.core import OneShotBehaviour
import spade
from turtle.agents.turtleAgent.goals import Goals

class TestIfOtherReady(OneShotBehaviour):
    otherReady = 1
    otherNonReady = 2
    otherCantPush = 3
    def process(self):
        if self.myAgent.getData("otherStatus") == Goals.otherStatus["ready"]:
            self._exitcode = TestIfOtherReady.otherReady
        elif self.myAgent.getData("otherStatus") == Goals.otherStatus["nonready"]:
            self._exitcode = TestIfOtherReady.otherNonReady
        else:
            self._exitcode = TestIfOtherReady.otherCantPush
