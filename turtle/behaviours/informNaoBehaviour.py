from community.core import OneShotBehaviour
import spade
import json

class InformNaoBehaviour(OneShotBehaviour):

    def process(self):
        message = spade.ACLMessage.ACLMessage()
        message.setPerformative("inform")
        message.setContent(json.dumps(self.myAgent.getData("currentGoal")))
        message.addReceiver(self.myAgent.getData("naoAid"))
        message.setOntology("turtleMove")
        self.myAgent.communicator.sendMessage(message)
        self._exitcode = 0