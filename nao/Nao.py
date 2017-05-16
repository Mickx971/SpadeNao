# -*- coding: utf-8 -*-

'''
Created on 28 April 2017
@author: Mickaël Lafages
@description: Nao respond to orders
'''
import naoutil.naoenv as naoenv
import naoutil.memory as memory
from community.core import Agent
from naoutil.broker import Broker
from fluentnao.nao import Nao
from community.statechart import EventFSMBehaviour
from community.behaviours.executor import TaskExecutor
from community.behaviours.system import SystemCore
from time import sleep
import qi
from threading import Lock


class NaoAgent(Agent):

    EVENT_ORDER_LISTEN = "EVENT_ORDER_LISTEN"
    EVENT_ORDER_SIT_DOWN = "EVENT_ORDER_SIT_DOWN"
    EVENT_ORDER_STAND_UP = "EVENT_ORDER_STAND_UP"
    EVENT_ORDER_SAY_HI = "EVENT_ORDER_SAY_HI"
    SALLE_1_RAPHAEL = "SALLE_1_RAPHAEL"
    SALLE_2_RAPHAEL = "SALLE_2_RAPHAEL"
    SALLE_3_RAPHAEL = "SALLE_3_RAPHAEL"

    def listenCall(myAgent):
        myAgent.log("listen Call", "LISTEN_CALL")

    def listenOrder(myAgent):
        myAgent.log("listenOrder", "LISTEN_ORDER")
        myAgent.say("J'écoute")

    def sitDown(myAgent):
        myAgent.log("sitDown", "SIT_DOWN")
        myAgent.nao.sit()
        return 0

    def standUp(myAgent):
        myAgent.log("standUp", "STAND_UP")
        myAgent.nao.stand()
        return 0

    def sayHi(myAgent):
        myAgent.log("sayHi", "SAY_HI")
        myAgent.sayAnimated("^start(animations/Stand/Gestures/Hey_1) Oui, je veux faire un coucou à tout le monde! ^wait(animations/Stand/Gestures/Hey_1)")
        return 0

    def createTurtleOrder(self, turtleName, orderName, data):
        def action(myAgent):
            myAgent.say(orderName)
        return action

    def __init__(self, name, host, secret, selfIP):

        speechEvents = dict()
        speechEvents["nao écoute moi"] = NaoAgent.EVENT_ORDER_LISTEN
        speechEvents["Veux-tu dire quelque chose ?"] = NaoAgent.EVENT_ORDER_SAY_HI
        speechEvents["Assieds-toi"] = NaoAgent.EVENT_ORDER_SIT_DOWN
        speechEvents["Mets-toi debout"] = NaoAgent.EVENT_ORDER_STAND_UP
        speechEvents["Raphael"] = NaoAgent.SALLE_1_RAPHAEL
        speechEvents["Donatello"] = NaoAgent.SALLE_1_RAPHAEL
        speechEvents["Dis à Raphael d'aller à la salle 2"] = NaoAgent.SALLE_2_RAPHAEL
        speechEvents["Dis à Raphael d'aller à la salle 3"] = NaoAgent.SALLE_3_RAPHAEL
        speechEvents["Ordonne d'aller dans la première salle"] = NaoAgent.SALLE_3_RAPHAEL
        speechEvents["Ordonne d'aller dans la deuxième salle"] = NaoAgent.SALLE_3_RAPHAEL
        speechEvents["Ordonne d'aller dans la troisième salle"] = NaoAgent.SALLE_3_RAPHAEL


        recognitionRate = dict()
        recognitionRate["nao écoute moi"] = .37
        recognitionRate["Assieds-toi"] = .40
        recognitionRate["Mets-toi debout"] = .35
        recognitionRate["Veux-tu dire quelque chose ?"] = .20
        recognitionRate["Dis à Raphael d'aller à la salle 1"] = .35
        recognitionRate["Dis à Raphael d'aller à la salle 2"] = .35
        recognitionRate["Dis à Raphael d'aller à la salle 3"] = .35

        # callbacks
        def recognitionCallback(dataName, value, message):

            d = dict(zip(value[0::2], value[1::2]))
            self.log(value[0] + " " + str(value[1]))

            self.log("acquire with listening: " + str(self.isListening), "recognitionCallback")
            self.lock.acquire()
            if not self.isListening :
                self.isListening = True
                self.lock.release()
                self.log("release 1", "recognitionCallback")
                return
            self.lock.release()
            self.log("release 2", "recognitionCallback")

            for word in d:
                if word in recognitionRate and d[word] > recognitionRate[word]:
                    self.raiseEvent(speechEvents[word])
                    return

            self.say("Je n'ai pas bien compris")

        def speechCallback(eventName, value, subscriberIdentifier):
            if value[1] in ["thrown", "stopped", "done"] and not self.isAnimatedSay:
                self.log("acquire 1", "speechCallback")
                self.lock.acquire()
                self.isListening = False
                self.lock.release()
                self.log("release 1", "speechCallback")

                sleep(2)
                self.log("acquire 2", "speechCallback")
                self.lock.acquire()
                self.isListening = True
                self.lock.release()
                self.log("release 2", "speechCallback")

        def animatedSpeechCallback(eventName, taskId, subscriberIdentifier):
            self.log("acquire 1", "animatedSpeechCallback")
            self.lock.acquire()
            self.isListening = False
            self.lock.release()
            self.log("release 1", "animatedSpeechCallback")

            sleep(4)
            self.log("acquire 2", "animatedSpeechCallback")
            self.lock.acquire()
            self.isListening = True
            self.lock.release()
            self.log("release 2", "animatedSpeechCallback")


        self.ip = selfIP
        self.broker = Broker('bootstrapBroker', naoIp=self.ip, naoPort=9559)

        # FluentNao
        self.nao = Nao(naoenv.make_environment(None))
        self.nao.env.tts.setLanguage("French")
        self.memory = memory

        self.lock = Lock()
        self.isListening = True

        vocabulary = []
        vocabulary.extend(speechEvents.keys())

        try:
            self.nao.env.speechRecognition.setVocabulary(vocabulary, True)
        except RuntimeError as e:
            self.log(e.message, "RuntimeError")

        self.memory.subscribeToEvent('WordRecognized', recognitionCallback)
        self.memory.subscribeToEvent('ALTextToSpeech/Status', speechCallback)
        self.memory.subscribeToEvent('ALAnimatedSpeech/EndOfAnimatedSpeech', animatedSpeechCallback)

        behaviours = [SystemCore(), TaskExecutor(), self.createEventFSMBehaviour()]

        Agent.__init__(self, name, host, secret, behaviours, [])

    def createEventFSMBehaviour(self):

        LISTEN_CALL = "LISTEN_CALL"
        LISTEN_ORDER = "LISTEN_ORDER"
        SIT_DOWN = "SIT_DOWN"
        STAND_UP = "STAND_UP"
        SAY_HI = "SAY_HI"
        RAPHAEL_SALLE_1 = "RAPHAEL_SALLE_1"
        RAPHAEL_SALLE_2 = "RAPHAEL_SALLE_2"
        RAPHAEL_SALLE_3 = "RAPHAEL_SALLE_3"

        evfsm = EventFSMBehaviour("Liveness")

        evfsm.createState(LISTEN_CALL, NaoAgent.listenCall)
        evfsm.createState(LISTEN_ORDER, NaoAgent.listenOrder)
        evfsm.createState(SIT_DOWN, NaoAgent.sitDown)
        evfsm.createState(STAND_UP, NaoAgent.standUp)
        evfsm.createState(SAY_HI, NaoAgent.sayHi)
        evfsm.createState(RAPHAEL_SALLE_1, self.createTurtleOrder("Raphael", "goTo", "salle1"))
        evfsm.createState(RAPHAEL_SALLE_2, self.createTurtleOrder("Raphael", "goTo", "salle1"))
        evfsm.createState(RAPHAEL_SALLE_3, self.createTurtleOrder("Raphael", "goTo", "salle1"))

        evfsm.createWaitingTransition(LISTEN_CALL, LISTEN_ORDER, NaoAgent.EVENT_ORDER_LISTEN)
        evfsm.createMultiChoiceWaitingTransition() \
            .fromState(LISTEN_ORDER) \
            .ifCondition(NaoAgent.EVENT_ORDER_SIT_DOWN).goTo(SIT_DOWN) \
            .elifCondition(NaoAgent.EVENT_ORDER_STAND_UP).goTo(STAND_UP) \
            .elifCondition(NaoAgent.EVENT_ORDER_SAY_HI).goTo(SAY_HI) \
            .elifCondition(NaoAgent.SALLE_1_RAPHAEL).goTo(RAPHAEL_SALLE_1) \
            .elifCondition(NaoAgent.SALLE_2_RAPHAEL).goTo(RAPHAEL_SALLE_2) \
            .elifCondition(NaoAgent.SALLE_2_RAPHAEL).goTo(RAPHAEL_SALLE_3) \
            .create()

        evfsm.createSimpleTransition(SIT_DOWN, LISTEN_CALL, 0)
        evfsm.createSimpleTransition(STAND_UP, LISTEN_CALL, 0)
        evfsm.createSimpleTransition(SAY_HI, LISTEN_CALL, 0)
        evfsm.createSimpleTransition(RAPHAEL_SALLE_1, LISTEN_CALL, 0)
        evfsm.createSimpleTransition(RAPHAEL_SALLE_2, LISTEN_CALL, 0)
        evfsm.createSimpleTransition(RAPHAEL_SALLE_3, LISTEN_CALL, 0)

        evfsm.setStartingPoint(LISTEN_CALL)

        return evfsm

    def log(self, msg, module=""):
        qi.logInfo(module, msg)

    def say(self, text):
        self.isAnimatedSay = False
        self.log(text)
        self.nao.say(text)

    def sayAnimated(self, text):
        self.isAnimatedSay = True
        self.log(text)
        self.nao.animate_say(text)

    def takeDown(self):
        print "TakeDown"
        self.memory.unsubscribeToEvent('WordRecognized')
        self.memory.unsubscribeToEvent('ALTextToSpeech/Status')
        self.memory.unsubscribeToEvent('ALAnimatedSpeech/EndOfAnimatedSpeech')
        self.broker.shutdown()
