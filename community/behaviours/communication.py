import spade
from community.core import Behaviour

class Sender (spade.Behaviour.Behaviour):
    def __init__(self):
        # super(Communicator, self).__init__("Communicator")
        spade.Behaviour.Behaviour.__init__(self)
        self.conversationId = 0

    def _process(self):
        pass

    def sendMessageAndWaitForResponce(self, message):
        print "from communicator: message to be sent"
        conversationId = message.getConversationId()
        self.myAgent.send(message)
        print "from communicator: message sent"
        message = self._receive(block=True)
        while message.getConversationId() != conversationId:
            message = self._receive(block=True)
        print "from communicator: message received"
        return message

    def sendMessage(self, message):
        self.myAgent.send(message)


class Receiver(spade.Behaviour.Behaviour):

    def __init__(self):
        #super(Communicator, self).__init__("Communicator")
        spade.Behaviour.Behaviour.__init__(self)
        self.conversationId = 0

    def _process(self):
        m = self._receive(block=True)
        print "message Received"
        m = spade.ACLMessage.ACLMessage()
        print m.getConversationId()