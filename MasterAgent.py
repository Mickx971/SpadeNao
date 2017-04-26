#from naoqi import ALProxy

#tts = ALProxy("ALTextToSpeech", "192.168.43.102", 9559)
#tts.say("Bonjour tout le monde!")
from community.builder import AgentBuilder
from community.stateChart import StateChart

if __name__ == "__main__":

    def printCoucou():
        print "action: coucou"

    def printBonjour():
        print "action: bonjour"

    def printHello():
        print "action: hello"

    def printHola():
        print "action: hola"

    def printAurevoir():
        print "Au revoir"

    def printSix():
        print "six"

    st = StateChart("Liveness")
    st.createState("first", printCoucou)
    st.createState("second", printBonjour)
    st.createState("third", printHello)
    st.createState("forth", printHola)
    st.createsSyncState("fith", printAurevoir)
    st.createState("six", printSix)
    st.createTransition("first", "second")
    st.createMultiChoiceTransition()\
        .fromState("second")\
            .ifCondition("condition(un)").goTo("third") \
            .elifCondition("condition(deux)").goTo("third")\
            .elseCondition().goTo("forth")\
        .create()
    st.createTransition("first", "fith")
    st.createTransition("forth", "fith")
    st.createTransition("fith", "six", "six")
    st.setStartingPoint("first")

    nao = AgentBuilder()\
        .setName("nao1")\
        .setPlatform("127.0.0.1")\
        .setSecret("secret")\
        .addTaskExcutor()\
        .addBehaviour(st)\
        .create()

    nao.start()
