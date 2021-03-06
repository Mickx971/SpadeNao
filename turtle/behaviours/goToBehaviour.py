from turtle.agents.turtleAgent.goals import Goals
from community.core import OneShotBehaviour
from turtle.services.navigationService import GoToPose

class GoToPoseBehaviour(OneShotBehaviour):
    GOAL_REACHED = 0
    GOAL_NON_REACHED = 0
    navigator = GoToPose()

    def process(self):
        print "GoToPoseBehaviour"
        pose = self.myAgent.getData("goals")["pose"]
        if GoToPoseBehaviour.navigator.goto(pose["position"], \
                                            pose["quaterion"]):
            self.myAgent.getData("currentGoal")["status"] = Goals.state["suceeded"]
            self._exitcode = GoToPoseBehaviour.GOAL_REACHED
            print  "goal reached"
        else:
            self.myAgent.getData("currentGoal")["status"] = Goals.state["failed"]
            self._exitcode = GoToPoseBehaviour.GOAL_NON_REACHED
            print "goal non reached"