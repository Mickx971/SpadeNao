#from naoqi import ALProxy

#tts = ALProxy("ALTextToSpeech", "192.168.43.102", 9559)
#tts.say("Bonjour tout le monde!")
from community.builder import AgentBuilder
from community.behaviours.dummy.PeriodicLogger import MainBehaviour
from community.stateChart import StateChart

if __name__ == "__main__":

    def printCoucou():
        print "coucou 1"

    def printBonjour():
        print "bonjour 2"

    def printHello():
        print "hello 3"

    def printHola():
        print "hola 4"

    st = StateChart("Livenes")
    st.createState("first", printCoucou)
    st.createState("second", printBonjour)
    st.createState("third", printHello)
    st.createState("forth", printHola)
    st.createTransition("first", "second")
    st.createMultiChoiceTransition()\
        .fromState("second")\
            .ifCondition("condition(un)").goTo("third") \
            .elifCondition("condition(deux)").goTo("third")\
            .elseCondition().goTo("forth")\
        .create()
    st.setStartingPoint("first")

    nao = AgentBuilder()\
        .setName("nao1")\
        .setPlatform("192.168.43.170")\
        .setSecret("secret")\
        .addTaskExcutor()\
        .addBehaviour(st)\
        .create()

    nao.start()
