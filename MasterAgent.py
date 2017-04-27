# -*- coding: utf-8 -*-
#from __future__ import print_function
# from naoutil import broker
# import naoutil.naoenv as naoenv
# import naoutil.memory as memory
# from fluentnao.nao import Nao
from community.statechart import EventFSMBehaviour
from community.builder import AgentBuilder
from community.statechart import TransitionCondition
from time import sleep

#########################
# SETUP
#########################

# Broker (must come first)
# naoIp = "192.168.43.102"
# broker.Broker('bootstrapBroker', naoIp=naoIp, naoPort=9559)

# # FluentNao
# env = naoenv.make_environment(None)
# log = lambda msg: print (msg)  # lambda for loggin to the console
# nao = Nao(env, log)


# def speechCallback(dataName, value, message):
#     print("qsdfqsdfsdfqsd")
#     d = dict(zip(value[0::2], value[1::2]))
#     t = .58
#     for word in d:
#         if d[word] > t:
#             # nao.say(word)
#             pass


EVENT_ORDER_LISTEN = "EVENT_ORDER_LISTEN"
EVENT_ORDER_SIT_DOWN = "EVENT_ORDER_SIT_DOWN"
EVENT_ORDER_STAND_UP = "EVENT_ORDER_STAND_UP"
EVENT_ORDER_SAY_HI = "EVENT_ORDER_SAY_HI"

def listenCall(myAgent):
    print "listen Call"
    # memory.unsubscribeToEvent('WordRecognized')
    # vocabulary = ["nao écoute moi"]
    # nao.env.speechRecognition.setVocabulary(vocabulary, False)
    # memory.subscribeToEvent('WordRecognized', speechCallback)


def listenOrder(myAgent):
    print "listen Order"
    # memory.unsubscribeToEvent('WordRecognized')
    # vocabulary = ["Assieds-toi", "Lève-toi", "Dis bonjour"]
    # nao.env.speechRecognition.setVocabulary(vocabulary, False)
    # memory.subscribeToEvent('WordRecognized', speechCallback)


def sitDown(myAgent):
    print "sit down"
    #nao.sit()


def standUp(myAgent):
    print "stand up"
    #nao.stand()


def sayHi(myAgent):
    print "say hi"
    #nao.animate_say("^start(animations/Stand/Gestures/Hey_1) Bonjour tout le monde! ^wait(animations/Stand/Gestures/Hey_1)")


if __name__ == "__main__":

    LISTEN_CALL = "LISTEN_CALL"
    LISTEN_ORDER = "LISTEN_ORDER"
    SIT_DOWN = "SIT_DOWN"
    STAND_UP = "STAND_UP"
    SAY_HI = "SAY_HI"

    st = EventFSMBehaviour("Liveness")

    st.createState(LISTEN_CALL, listenCall)
    st.createState(LISTEN_ORDER, listenOrder)
    st.createState(SIT_DOWN, sitDown)
    st.createState(STAND_UP, standUp)
    st.createState(SAY_HI, sayHi)

    st.createTransition(LISTEN_CALL, LISTEN_ORDER, TransitionCondition(EVENT_ORDER_LISTEN, "coucou"))

    st.createMultiChoiceTransition()\
        .fromState(LISTEN_ORDER)\
            .ifCondition(TransitionCondition(EVENT_ORDER_SIT_DOWN, "bonjour")).goTo(SIT_DOWN) \
            .elifCondition(EVENT_ORDER_STAND_UP).goTo(STAND_UP)\
            .elifCondition(EVENT_ORDER_SAY_HI).goTo(SAY_HI)\
        .create()

    st.createTransition(SIT_DOWN, LISTEN_CALL)
    st.createTransition(STAND_UP, LISTEN_CALL)
    st.createTransition(SAY_HI, LISTEN_CALL)

    st.setStartingPoint(LISTEN_CALL)

    naoAgent = AgentBuilder()\
        .setName("nao1")\
        .setPlatform("127.0.0.1")\
        .setSecret("secret")\
        .addTaskExcutor()\
        .addBehaviour(st)\
        .create()

    naoAgent.start()
