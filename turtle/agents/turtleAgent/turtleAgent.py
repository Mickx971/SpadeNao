from community.core import Agent
import json
from communicator import Communicator, Receiver

class TurtleAgent(Agent):

    def __init__(self, name, host, password, receiveBehaviour = Receiver()):
        self.communicator = Communicator()
        self.communicator._receiver = receiveBehaviour
        Agent.__init__(self, name, host, password, self.communicator.getBehaviours(), [])
        with open("knowledge.json") as knowledge:
             self.setData("knowledge", json.load(knowledge)[self.localName])
        self.setData("goals", {"pose": {}})




if __name__ == "__main__":
    agent = TurtleAgent("turtle1", "127.0.0.1", "secret", [])
    agent.start()

