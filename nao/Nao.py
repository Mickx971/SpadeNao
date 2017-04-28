# -*- coding: utf-8 -*-

'''
Created on 28 April 2017
@author: Mickaël Lafages
@description: Nao respond to orders
'''

from __future__ import print_function
import naoutil.naoenv as naoenv
import naoutil.memory as memory
from community.core import Agent
from naoutil.broker import Broker
from fluentnao.nao import Nao
from community.statechart import EventFSMBehaviour
from community.behaviours.executor import TaskExecutor
from community.behaviours.system import SystemCore


class NaoAgent(Agent):

    EVENT_ORDER_LISTEN = "EVENT_ORDER_LISTEN"
    EVENT_ORDER_SIT_DOWN = "EVENT_ORDER_SIT_DOWN"
    EVENT_ORDER_STAND_UP = "EVENT_ORDER_STAND_UP"
    EVENT_ORDER_SAY_HI = "EVENT_ORDER_SAY_HI"

    def __init__(self, name, host, secret, selfIP):


        speechEvents = dict()
        speechEvents["nao écoute moi"] = NaoAgent.EVENT_ORDER_LISTEN
        speechEvents["Assieds-toi"] = NaoAgent.EVENT_ORDER_SIT_DOWN
        speechEvents["Lève-toi"] = NaoAgent.EVENT_ORDER_STAND_UP
        speechEvents["Dis bonjour"] = NaoAgent.EVENT_ORDER_SAY_HI

        # callbacks
        def speechCallback(dataName, value, message):
            self.nao.log("qsdfqsdfsdfqsd")
            d = dict(zip(value[0::2], value[1::2]))
            t = .25
            for word in d:
                if d[word] > t:
                    if word in speechEvents:
                        self.memory.unsubscribeToEvent('WordRecognized')
                        self.raiseEvent(speechEvents[word])
                        break
            else:
                self.nao.say("Je n'ai pas bien compris")

        def listenCall(myAgent):
            print("listen Call")
            myAgent.memory.unsubscribeToEvent('WordRecognized')
            vocabulary = ["nao écoute moi"]
            myAgent.nao.env.speechRecognition.pause(True)
            myAgent.nao.env.speechRecognition.setVocabulary(vocabulary, False)
            myAgent.memory.subscribeToEvent('WordRecognized', speechCallback)

        def listenOrder(myAgent):
            print("listen Order")
            myAgent.memory.unsubscribeToEvent('WordRecognized')
            vocabulary = ["Assieds-toi", "Lève-toi", "Dis bonjour"]
            myAgent.nao.env.speechRecognition.pause(True)
            myAgent.nao.env.speechRecognition.setVocabulary(vocabulary, False)
            myAgent.memory.subscribeToEvent('WordRecognized', speechCallback)
            pass

        def sitDown(myAgent):
            print("sit down")
            myAgent.nao.sit()
            return 0

        def standUp(myAgent):
            print("stand up")
            myAgent.nao.stand()
            return 0

        def sayHi(myAgent):
            print("say hi")
            myAgent.nao.animate_say("^start(animations/Stand/Gestures/Hey_1) Bonjour tout le monde! ^wait(animations/Stand/Gestures/Hey_1)")
            return 0

        activities = dict()
        activities["listenCall"] = listenCall
        activities["listenOrder"] = listenOrder
        activities["sitDown"] = sitDown
        activities["sayHi"] = sayHi
        activities["standUp"] = standUp

        behaviours = list()
        behaviours.append(self.createEventFSMBehaviour(activities))
        behaviours.append(SystemCore())
        behaviours.append(TaskExecutor())

        Agent.__init__(self, name, host, secret, behaviours, [])

        self.ip = selfIP
        self.broker = Broker('bootstrapBroker', naoIp=self.ip, naoPort=9559)

        # FluentNao
        self.nao = Nao(naoenv.make_environment(None), lambda msg: print(msg))
        self.nao.env.tts.setLanguage("French")
        self.memory = memory

    def createEventFSMBehaviour(self, activities):

        LISTEN_CALL = "LISTEN_CALL"
        LISTEN_ORDER = "LISTEN_ORDER"
        SIT_DOWN = "SIT_DOWN"
        STAND_UP = "STAND_UP"
        SAY_HI = "SAY_HI"

        evfsm = EventFSMBehaviour("Liveness")

        evfsm.createState(LISTEN_CALL, activities["listenCall"])
        evfsm.createState(LISTEN_ORDER, activities["listenOrder"])
        evfsm.createState(SIT_DOWN, activities["sitDown"])
        evfsm.createState(STAND_UP, activities["standUp"])
        evfsm.createState(SAY_HI, activities["sayHi"])

        evfsm.createWaitingTransition(LISTEN_CALL, LISTEN_ORDER, NaoAgent.EVENT_ORDER_LISTEN)
        evfsm.createMultiChoiceWaitingTransition() \
            .fromState(LISTEN_ORDER) \
            .ifCondition(NaoAgent.EVENT_ORDER_SIT_DOWN).goTo(SIT_DOWN) \
            .elifCondition(NaoAgent.EVENT_ORDER_STAND_UP).goTo(STAND_UP) \
            .elifCondition(NaoAgent.EVENT_ORDER_SAY_HI).goTo(SAY_HI) \
            .create()

        evfsm.createSimpleTransition(SIT_DOWN, LISTEN_CALL, 0)
        evfsm.createSimpleTransition(STAND_UP, LISTEN_CALL, 0)
        evfsm.createSimpleTransition(SAY_HI, LISTEN_CALL, 0)

        evfsm.setStartingPoint(LISTEN_CALL)

        return evfsm

    def takeDown(self):
        print("TakeDown")
        memory.unsubscribeToEvent('WordRecognized')
        self.broker.shutdown()
