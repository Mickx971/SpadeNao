import spade
from spade import DF
from spade import AID
from community.core import Behaviour


class SystemCore(Behaviour):
    def __init__(self):
        template = spade.Behaviour.ACLTemplate()
        template.setOntology("system")
        super(SystemCore, self).__init__("System", spade.Behaviour.MessageTemplate(template))
        self.actions = dict()
        self.actions["stop"] = self.stopAgent

    def stopAgent(self):
        self.myAgent.stop()

    def onStart(self):
        print "Core behaviour started"

    def onEnd(self):
        print "Core behaviour ended"

    def process(self):
        msg = self._receive(True)
        if msg is not None:
            action = self.actions.get(msg.getContent())
            if action is not None:
                action()
            else:
                print "SystemCore: no action named ", msg.getContent()
