from collections import defaultdict
from community.core import Behaviour
from spade.ACLMessage import ACLMessage
from spade.AID import aid
import random
import spade
import json


class Communicator(Behaviour):
    def __init__(self):
        template = spade.Behaviour.MessageTemplate(spade.Behaviour.ACLTemplate())
        super(Communicator, self).__init__("Communicator", template)
        self.aids = dict()
        self.ontologyActions = defaultdict(lambda: None)

    def getSenderName(self, sender):
        for item in self.aids.iteritems():
            if item[1].getName() == sender.getName():
                return item[0]
        return None

    def getOtherTurtleName(self, turtleName):
        for turtle in self.aids.iterkeys():
            if turtle != turtleName:
                return turtle
        return None

    def onHumanMoveMessage(self, aclMessage):
        self.myAgent.log("Sender: " + aclMessage.getSender().getName() + " Content: " + aclMessage.getContent(), "Communicator")
        self.myAgent.raiseEvent("EVENT_MOVE", aclMessage)

    def onTurtleMove(self, aclMessage):
        self.myAgent.log("Sender: " + aclMessage.getSender().getName() + " Content: " + aclMessage.getContent(), "Communicator")
        self.myAgent.raiseEvent("EVENT_TURTLE_MOVE", aclMessage)

    def onTurlePush(self, aclMessage):
        self.myAgent.log("Sender: " + aclMessage.getSender().getName() + " Content: " + aclMessage.getContent(), "Communicator")
        self.myAgent.raiseEvent("EVENT_TURTLE_PUSH", aclMessage)

    def onStart(self):
        print "Communicator behaviour started"
        self.aids["samira"] = aid("samira@" + self.myAgent.host, ["xmpp://" + "samira@" + self.myAgent.host])
        self.aids["raphael"] = aid("raphael@" + self.myAgent.host, ["xmpp://" + "raphael@" + self.myAgent.host])

        self.ontologyActions["turtleMove"] = self.onTurtleMove
        self.ontologyActions["turtlePush"] = self.onTurlePush
        self.ontologyActions["cameraOntology"] = self.onHumanMoveMessage

    def onEnd(self):
        print "Communicator behaviour ended"

    def process(self):

        msg = self._receive(True)
        if msg is not None:
            try:
                ontologyAction = self.ontologyActions[msg.getOntology()]
                if ontologyAction is not None:
                    ontologyAction(msg)
                else:
                    self.myAgent.log("No action for ontology: " + msg.getOntology(), "Communicator")
            except ValueError:
                pass

    def sendMoveOrder(self, turtleName, destinationName):
        msg = ACLMessage()
        msg.setOntology("turtleMove")
        msg.setPerformative("request")
        msg.setContent(destinationName)
        msg.addReceiver(self.aids[turtleName])
        self.myAgent.log(msg)
        self.myAgent.send(msg)

    def sendPushOrder(self):
        msg = ACLMessage()
        msg.setOntology("turtlePush")
        msg.setPerformative("request")
        msg.setContent("")
        turtles = list()
        turtles.extend(self.aids.values())
        msg.addReceiver(turtles[random.randint(0, 1)])
        self.myAgent.send(msg)

    def sendGetherOrder(self):
        msg = ACLMessage()
        msg.setOntology("turtleMove")
        msg.setPerformative("request")
        msg.setContent("goNear")
        turtles = list()
        turtles.extend(self.aids.values())
        turtle = self.aids["samira"]
        self.myAgent.log(turtle.getName(),"GETHER")
        msg.addReceiver(turtle)
        self.myAgent.send(msg)

