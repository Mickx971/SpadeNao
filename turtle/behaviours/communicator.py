from turtle.services.positionService import PositionService
import spade
import json
from community.core import Behaviour
class Communicator(Behaviour):

    def process(self):
        msg = self._receive(block=True)
        self.givePosition(msg)

    def givePosition(self, msg):
        if msg.getContent() is not None and\
            "position" in msg.getContent() and\
            msg.getSender() is not None:
            (trans, rot) = PositionService.getCurrentPosition()
            print trans,rot
            message = {}
            message["position"] = trans
            message["quaterion"] = rot
            message = json.dumps(message)
            response = spade.ACLMessage.ACLMessage()
            response.setPerformative("inform")
            response.setOntology("position")
            response.addReceiver(msg.getSender())
            response.setContent(message)
            response.setConversationId(msg.getConversationId())
            self.myAgent.send(response)