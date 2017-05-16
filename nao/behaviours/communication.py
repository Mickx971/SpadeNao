from collections import defaultdict
from community.core import Behaviour
import spade
import json


class Communicator(Behaviour):
    def __init__(self):
        template = spade.Behaviour.MessageTemplate(spade.Behaviour.ACLTemplate())
        super(Communicator, self).__init__("Communicator", template)

        self.actions = defaultdict(lambda: defaultdict(lambda: None))
        self.actions["turtleOntology"] = defaultdict(lambda: None)
        self.actions["turtleOntology"]["turtleSay"] = self.onTurtleSay

        self.actions["cameraOntology"] = defaultdict(lambda: None)
        self.actions["cameraOntology"]["humanMove"] = self.onHumanMoveMessage

    def onHumanMoveMessage(self, aclMessage, jsonContent):
        self.myAgent.log(jsonContent)
        self.myAgent.raiseEvent("EVENT_MOVE", jsonContent)

    def onTurtleSay(self, aclMessage, jsonContent):
        self.myAgent.log(jsonContent)
        self.myAgent.raiseEvent("EVENT_TURTLE_SAY", jsonContent)

    def onStart(self):
        print "Communicator behaviour started"

    def onEnd(self):
        print "Communicator behaviour ended"

    def process(self):

        def ascii_encode_dict(data):
            return dict(map(lambda x: x.encode('ascii'), pair) for pair in data.items())

        msg = self._receive(True)
        if msg is not None:
            try:
                msgContent = json.loads(msg.getContent(), object_hook=ascii_encode_dict)
                if "event" in msgContent:
                    action = self.actions[msg.getOntology()][msgContent["event"]]
                    if action is not None:
                        action(msg, msgContent)
                    else:
                        self.myAgent.log("Communicator: no action for content: " + msg.getContent())
            except ValueError:
                pass
