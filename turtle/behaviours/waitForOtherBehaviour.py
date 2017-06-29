import spade
from community.core import Behaviour, Agent
class agentBehaviour(Behaviour):

    def process(self):
		"""template = spade.Behaviour.ACLTemplate()
		template.setOntology("stop")
		mt = spade.Behaviour.MessageTemplate(template)"""
		msg = self._receive(block=True)
		#print mt.match(msg)
		print "messageReceived"




class PyAgent(Agent):
    def _setup(self):
        #template = spade.Behaviour.ACLTemplate()
        #template.setOntology("stop")
        #mt = spade.Behaviour.MessageTemplate(template)
		print "agent starting"
		self.addBehaviour(agentBehaviour("nom"), None)

if __name__ == "__main__":
    a = PyAgent("py", "127.0.0.1", "secret", [], [])
    a.start()