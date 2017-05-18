from community.core import Agent
import json
from communicator import Communicator, Receiver
import spade
from goals import Goals

from community.behaviours.system import SystemCore
class TurtleAgent(Agent):

    def __init__(self, name, host, password, receiveBehaviour = Receiver()):
        self.communicator = Communicator()
        self.communicator._receiver = receiveBehaviour
        behaviours = self.communicator.getBehaviours()
        behaviours.append(SystemCore())
        Agent.__init__(self, name, host, password, behaviours, [])
        with open("knowledge.json") as knowledge:
             self.setData("knowledge", json.load(knowledge)[self.localName])
        self.setData("goals", {"pose": {}})
        self.setData("naoAid",spade.AID.aid("nao1@"+host,
                                 ["xmpp://nao1@"+host]))
        other = self.getData("knowledge")["other"] + "@" + host
        otherAid = spade.AID.aid(other, ["xmpp://" + other])
        self.setData("otherTurtleAid", otherAid)
        self.setData("otherState", Goals.otherStatus["nonReady"])




if __name__ == "__main__":
    agent = TurtleAgent("raphael", "127.0.0.1", "secret", [])
    agent.start()

