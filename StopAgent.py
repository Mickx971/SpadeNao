import sys
import spade


class AgentKiller(spade.Agent.Agent):

    class Kill(spade.Behaviour.OneShotBehaviour):
        def _process(self):
            try:
                receiver = spade.AID.aid(name=self.myAgent.victim, addresses=["xmpp://" + self.myAgent.victim])
                self.myAgent.msg.addReceiver(receiver)
                self.myAgent.send(self.myAgent.msg)
                self.myAgent.stop()
            except Exception as e:
                print "Unexpected error:", type(e)
                print e

    def setVictim(self, victim):
        self.victim = victim

    def _setup(self):
        self.msg = spade.ACLMessage.ACLMessage()  # Instantiate the message
        self.msg.setPerformative("request")
        self.msg.setOntology("system")
        self.msg.setContent("stop")
        self.addBehaviour(self.Kill())

if __name__ == "__main__":

    if len(sys.argv) != 2:
        raise RuntimeError("No victim to kill")

    killer = AgentKiller("killer@127.0.0.1", "secret")
    killer.setVictim(sys.argv[1])
    killer.start()
