from turtle.agents.turtleAgent.goals import  Goals
from community.core import OneShotBehaviour
class WaitMessageBehaviour(OneShotBehaviour):

    goTo = 0
    goNear = 1
    naoSaidToPushTheBox = 2
    turtleSaidToPushTheBox = 3

    def process(self):
        print "wait for message behaviour"
        while True:
            message = self.myAgent.communicator.waitForMessage(None)
            print "waitForMessageBehaviour", message.getContent(), message.getOntology(), message.getPerformative()
            if message.getOntology() == "turtleMove" and message.getPerformative() == "request":
                content = message.getContent()
                print "first if"
                if content in self.myAgent.getData("knowledge")["pose"].keys():
                    self.myAgent.setData("goals", {"pose": self.myAgent.getData("knowledge")["pose"][content]})
                    self.myAgent.setData("currentGoal", {"status": Goals.state["inProgress"],
                                                         "action": content})
                    self._exitcode = WaitMessageBehaviour.goTo
                    print "second if"
                    break

                if content == "goNear":
                    self.myAgent.setData("currentGoal", {"state": Goals.state["inProgress"],
                                                         "action": "goNear"})
                    self._exitcode = WaitMessageBehaviour.goNear
                    break

            """if message.getOntology() is not None and message.getOntology() == "pushTheBox":
                if message.getSender() == self.myAgent.getData("naoAid"):
                    self.myAgent.setData("goals", {"pose": self.myAgent.getData("knowledge")["pose"]["nearTheBox"]})
                    self.myAgent.setData("currentGoal", {"status": Goals.state["inProgress"],
                                                         "action": "pushTheBox",
                                                         "tellTheNao": Goals.tellTheNao["mustTellTheNao"]})
                    self._exitcode = WaitMessageBehaviour.naoSaidToPushTheBox
                    break

                if message.getSender() == self.myAgent.getData("otherTurtleAid"):
                    self.myAgent.setData("goals", {"pose": self.myAgent.getData("knowledge")["pose"]["nearTheBox"]})
                    self.myAgent.setData("currentGoal", {"status": Goals.state["inProgress"],
                                                         "action": "pushTheBox",
                                                         "tellTheNao": Goals.tellTheNao["mustNotTellTheNao"]})
                    self._exitcode = WaitMessageBehaviour.turtleSaidToPushTheBox
                    break"""







        print "wait for message behaviour exited"
