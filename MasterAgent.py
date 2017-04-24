import spade
import sys
#from naoqi import ALProxy
from community.Agent import Agent


class MainBehaviour(spade.Behaviour.PeriodicBehaviour):
    def __init__(self):
        super(MainBehaviour, self).__init__(1)
        self.tick = 0

    def _onTick(self):
        self.tick = self.tick + 1
        try:
            print self.tick
        except:
            print "Ex1"
            print "Unexpected error:", sys.exc_info()[0]


class MasterAgent(Agent):

    def __init__(self, name, host, secret):
        super(Agent, self).__init__(name + "@" + host, secret)
        self.host = host

    def initAgent(self):
        #tts = ALProxy("ALTextToSpeech", "192.168.43.102", 9559)
        #tts.say("Bonjour tout le monde!")
        self.addBehaviour(MainBehaviour())


if __name__ == "__main__":
    nao = MasterAgent("nao1", "192.168.43.170", "secret")
    nao.start()
