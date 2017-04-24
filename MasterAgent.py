#from naoqi import ALProxy

#tts = ALProxy("ALTextToSpeech", "192.168.43.102", 9559)
#tts.say("Bonjour tout le monde!")


if __name__ == "__main__":

    from community.builder import AgentBuilder
    from community.behaviours.dummy.PeriodicLogger import MainBehaviour

    nao = AgentBuilder()\
        .setName("nao1")\
        .setPlatform("192.168.43.170")\
        .setSecret("secret")\
        .addBehaviour(MainBehaviour())\
        .addFact("bonjour(mickael)")\
        .create()

    nao.start()
