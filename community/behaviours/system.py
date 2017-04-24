import spade
from spade import DF
from spade import AID
from community.core import Behaviour


class SystemCore(Behaviour):
    def __init__(self):
        super(SystemCore, self).__init__("System", "system")
        self.actions = dict()
        self.actions["stop"] = self.stopAgent
        self.actions["registerToJadePlatform"] = self.registerToJadePlatform
        self.actions["deregisterToJadePlatform"] = self.deregisterToJadePlatform

    def stopAgent(self):
        self.myAgent.stop()

    def registerToJadePlatform(self):
        print "REGISTER BEHAV"
        # Register service in DF
        sd = DF.ServiceDescription()
        sd.setName("EXTERNAL_SERVICE")
        sd.setType("organization")
        sd.addProperty("topology", "coallition")
        dad = DF.DfAgentDescription()
        dad.addService(sd)
        dad.setAID(self.myAgent.getAID())
        # print dad
        otherdf = AID.aid("df@" + self.myAgent.host + ":1099/JADE", ["http://" + self.myAgent.host + ":7778/acc"])
        res = self.myAgent.registerService(dad, otherdf=otherdf)
        print "DF Register sent: ", str(res)

    def deregisterToJadePlatform(self):
        print "DEREGISTER BEHAV"
        # Register service in DF
        sd = DF.ServiceDescription()
        sd.setName("EXTERNAL_SERVICE")
        sd.setType("organization")
        sd.addProperty("topology", "coallition")
        dad = DF.DfAgentDescription()
        dad.addService(sd)
        dad.setAID(self.myAgent.getAID())
        # print dad
        otherdf = AID.aid("df@" + self.myAgent.host + ":1099/JADE", ["http://" + self.myAgent.host + ":7778/acc"])
        res = self.myAgent.deregisterService(dad, otherdf=otherdf)
        print "DF Register sent: ", str(res)

    def onStart(self):
        print "Core behaviour started"
        self.registerToJadePlatform()

    def onEnd(self):
        self.deregisterToJadePlatform()
        print "Core behaviour ended"

    def _process(self):
        try:
            msg = self._receive(True)
            if msg is not None:
                print msg.getSender()
                for receiver in msg.getReceivers():
                    print receiver
                action = self.actions.get(msg.getContent())
                if action is not None:
                    action()
        except Exception as e:
            print "Core:"
            print "Unexpected error:", type(e)
            print e