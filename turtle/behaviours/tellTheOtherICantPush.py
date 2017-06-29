from community.core import OneShotBehaviour
import spade
from turtle.agents.turtleAgent.goals import Goals
class TellOtherICantPush(OneShotBehaviour):

    def process(self):
        message = spade.ACLMessage.ACLMessage()
        message.setPerformative("inform")
        message.setOntology("pushTheBox")
        message.setContent(Goals.otherStatus["cantPush"])
        message.addReceiver(self.myAgent.getData("otherTurtleAid"))
        self.myAgent.communicator.sendMessage(message)
