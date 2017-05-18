from turtle.services.positionService import PositionService
import spade
import json
from community.core import Behaviour
from turtle.agents.turtleAgent.goals import Goals
class Communicator(Behaviour):

    def __init__(self):
        template = spade.Behaviour.ACLTemplate()
        mt = spade.Behaviour.MessageTemplate(template)
        Behaviour.__init__(self,"__receiver", mt)

    def process(self):
        msg = self._receive(block=True)
        self.givePosition(msg)
        self.otherReady(msg)

    def givePosition(self, msg):
        if msg.getOntology() is not None and msg.getOntology() == "position" \
                and msg.getPerformative() is not None and msg.getPerformative() == "request" \
                and msg.getSender() is not None:
            print "giving the position"
            message = PositionService.getCurrentPositionAsMap()
            message = json.dumps(message)
            response = spade.ACLMessage.ACLMessage()
            response.setPerformative("inform")
            response.setOntology("position")
            response.addReceiver(msg.getSender())
            response.setContent(message)
            response.setConversationId(msg.getConversationId())
            self.myAgent.send(response)

    def otherReady(self, msg):
        msg = spade.ACLMessage.ACLMessage()
        if msg.getOntology() is not None and msg.getPerformative() is not None\
            and msg.getPerformative() == "inform" and msg.getOntology() == "pushTheBox":
            if msg.getContent() == Goals.otherStatus["ready"]:
                self.myAgent.setData("otherStatus", Goals.otherStatus["ready"])
            elif msg.getContent() == Goals.otherStatus["cantPush"]:
                self.myAgent.setData("otherStatus", Goals.otherStatus["cantPush"])
