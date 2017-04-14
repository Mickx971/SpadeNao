import sys
import spade
from community.Agent import Agent


class AgentKiller(Agent):

    def __init__(self, name, secret):
        super(AgentKiller, self).__init__(name, secret)
        self.msg = spade.ACLMessage.ACLMessage()  # Instantiate the message
        self.msg.setPerformative("request")
        self.msg.setOntology("system")
        self.msg.setContent("stop")
        self.victim = None

    def setVictim(self, victim):
        self.victim = victim

    def initAgent(self):
        print self.victim
        receiver = spade.AID.aid(name=self.victim, addresses=["xmpp://" + self.victim])
        self.msg.addReceiver(receiver)
        self.send(self.msg)
        self.stop()

if __name__ == "__main__":
    killer = AgentKiller("killer@192.168.43.170", "secret")
    killer.setVictim(sys.argv[1])
    killer.start()
