from turtle.behaviours.getPositionBehaviour import GetPositionBehaviour
from turtle.services.positionService import PositionService
from turtle.agents.turtleAgent.goals import Goals
class TestIfNearOtherBehaviour(GetPositionBehaviour):

    Near = 0
    NotNear = 1
    def process(self):
        currentPosition = PositionService.getCurrentPositionAsMap()["position"]
        otherPosition = self.getAgentPosition(self.myAgent.getData("otherTurtleAid"))["position"]

        print "current position", currentPosition
        print "other position", otherPosition
        dist = (otherPosition["x"] - currentPosition["x"])\
               *(otherPosition["x"] - currentPosition["x"]) \
               + \
               (otherPosition["y"] - currentPosition["y"]) \
               * (otherPosition["y"] - currentPosition["y"])
        if dist < 1:
            self.myAgent.getData("currentGoal")["status"] = Goals.state["suceeded"]
            self._exitcode = TestIfNearOtherBehaviour.Near
        else:
            self.myAgent.getData("currentGoal")["status"] = Goals.state["failed"]
            self._exitcode = TestIfNearOtherBehaviour.NotNear
