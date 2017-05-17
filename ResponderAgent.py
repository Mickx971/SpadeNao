import spade


class RespondBehaviour(spade.Behaviour.Behaviour):
    def _process(self):
        message = self._receive(block=True)

        print "received", message.getConversationId()
        msg = spade.ACLMessage.ACLMessage()
        msg.setContent("content")
        msg.addReceiver(message.getSender())
        msg.setPerformative("inform")
        msg.setConversationId(message.getConversationId())
        #self.myAgent.send(msg)


class RespondAgent(spade.Agent.Agent):
    def _setup(self):
        print "starting"
        template = spade.Behaviour.ACLTemplate()
        mt = spade.Behaviour.MessageTemplate(template)
        self.addBehaviour(RespondBehaviour(), mt)


if __name__ == "__main__":
    agent = RespondAgent("test@127.0.0.1", "secret")
    agent.start()