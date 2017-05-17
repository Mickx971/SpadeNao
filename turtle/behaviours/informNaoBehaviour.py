from community.core import OneShotBehaviour
import spade
import json

class InformNaoBehaviour(OneShotBehaviour):
    naoAid = spade.AID.aid("agent1@127.0.0.1",
                                 ["xmpp://agent1@127.0.0.1"])
    def process(self):
        message = spade.ACLMessage.ACLMessage()
        message.setPerformative("inform")
        message.setContent(json.dumps(self.myAgent.getData("currentGoal")))
        message.addReceiver(InformNaoBehaviour.naoAid)
        self.myAgent.communicator.sendMessage(message)
