import spade
from community.core import Behaviour

class Sender (Behaviour):

    def __init__(self):
        template = spade.Behaviour.ACLTemplate()
        mt = spade.Behaviour.MessageTemplate(template)
        Behaviour.__init__(self,"__sender", mt)

    def sendMessageAndWaitForResponse(self, message):
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

    def waitForMessage(self, template):
        return self._receive(block=True, template=template)


class Receiver(Behaviour):

    def __init__(self):
        template = spade.Behaviour.ACLTemplate()
        mt = spade.Behaviour.MessageTemplate(template)
        Behaviour.__init__(self,"__receiver", mt)

    def process(self):
        m = self._receive(block=True)
        print "message Received"
        m = spade.ACLMessage.ACLMessage()
        print m.getConversationId()

class Communicator:
    def __init__(self):
        self._receiver = Receiver()
        self._sender = Sender()

    def sendMessageAndWaitForResponse(self, message):
        return self._sender.sendMessageAndWaitForResponse(message)

    def sendMessage(self, message):
        self._sender.sendMessage(message)

    def getBehaviours(self):
        return  [self._receiver, self._sender]

    def waitForMessage(self, template):
        return self._sender.waitForMessage(template)