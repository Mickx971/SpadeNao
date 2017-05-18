from community.core import OneShotBehaviour
import spade

class TellTheOtherToPrepareToPush(OneShotBehaviour):

    def process(self):
        message = spade.ACLMessage.ACLMessage()
        message.setPerformative("request")
        message.setOntology("pushTheBox")
        message.addReceiver(self.myAgent.getData("otherTurtleAid"))
        self.myAgent.communicator.sendMessage(message)
