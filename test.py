import spade
import time
from community.behaviours.communication import Sender, Receiver


class TestBehaviour(spade.Behaviour.OneShotBehaviour):
    def _process(self):
        try:
            communicator = self.myAgent.communicator
            message = spade.ACLMessage.ACLMessage()
            message.addReceiver(spade.AID.aid("test@127.0.0.1",
                                     ["xmpp://test@127.0.0.1"]))
            message.setPerformative("inform")
            communicator.sendMessageAndWaitForResponce(message)
            print "the message was received"
        except:
            print "uncaught exception"


class TestAgent(spade.Agent.Agent):

    def _setup(self):
        print "hi"
        self.communicator = Sender()
        template = spade.Behaviour.ACLTemplate()
        mt = spade.Behaviour.MessageTemplate(template)
        print "here"
        self.addBehaviour(Receiver(), mt)
        self.addBehaviour(self.communicator, mt)
        self.addBehaviour(TestBehaviour(), None)








if __name__ == "__main__" :
    agent = TestAgent("communicaton@127.0.0.1", "secret")
    agent.start()