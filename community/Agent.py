import spade


class Agent(spade.Agent.Agent):

    class CoreBehaviour(spade.Behaviour.Behaviour):
        def __init__(self):
            super(Agent.CoreBehaviour, self).__init__()
            self.actions = dict()
            self.actions["stop"] = self.stopAgent

        def stopAgent(self):
            self.myAgent.stop()

        def onStart(self):
            print "Core behaviour started"

        def _process(self):
            msg = self._receive(True)
            action = self.actions.get(msg.getContent())
            if action is not None:
                action()

    def initAgent(self):
        pass

    def _setup(self):
        template = spade.Behaviour.ACLTemplate()
        template.setOntology("system")
        mt = spade.Behaviour.MessageTemplate(template)
        self.addBehaviour(Agent.CoreBehaviour(), mt)
        self.initAgent()

