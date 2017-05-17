from turtle.agents.turtleAgent.goals import  Goals
from community.core import OneShotBehaviour
class WaitMessageBehaviour(OneShotBehaviour):

    goTo = 0
    goNear = 0

    def process(self):
        print "wait for message behaviour"
        while True:
            message = self.myAgent.communicator.waitForMessage(None)
            content = message.getContent()
            if content in self.myAgent.getData("knowledge")["pose"].keys():
                self.myAgent.setData("goals", {"pose": self.myAgent.getData("knowledge")["pose"][content]})
                self.myAgent.setData("currentGoal", {"state": Goals.state["inProgress"],
                                                     "action": WaitMessageBehaviour.goTo})
                self._exitcode = WaitMessageBehaviour.goTo
                break

            if content == "goNear":
                self.myAgent.setData("currentGoal", {"state": Goals.state["inProgress"],
                                                     "action": WaitMessageBehaviour.goNear})
                self._exitcode = WaitMessageBehaviour.goNear
                break

        print "wait for message behaviour exited"
