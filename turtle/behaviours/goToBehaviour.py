import spade
from community.core import OneShotBehaviour
from turtle.services.navigationService import GoToPose

class GoToPoseBehaviour(OneShotBehaviour):
    GOAL_REACHED = 0
    GOAL_NON_REACHED = 0
    navigator = GoToPose()

    def process(self):
        print "Move to pose behaviour"
        pose = self.myAgent.getData("goals")["pose"]
        if GoToPoseBehaviour.navigator.goto(pose["position"], \
                                            pose["quaterion"]):

            self._exitcode = GoToPoseBehaviour.GOAL_REACHED
            print  "goal reached"
        else:
            self._exitcode = GoToPoseBehaviour.GOAL_NON_REACHED
            print "goal non reached"