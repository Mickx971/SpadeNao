#from naoqi import ALProxy

#tts = ALProxy("ALTextToSpeech", "192.168.43.102", 9559)
#tts.say("Bonjour tout le monde!")
from community.builder import AgentBuilder
from community.behaviours.dummy.PeriodicLogger import MainBehaviour

if __name__ == "__main__":

    nao = AgentBuilder()\
        .setName("nao1")\
        .setPlatform("192.168.43.170")\
        .setSecret("secret")\
        .addBehaviour(MainBehaviour())\
        .create()

    nao.start()
