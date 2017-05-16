# -*- coding: utf-8 -*-

'''
Created on 28 April 2017
@author: Mickaël Lafages
@description: Nao respond to orders
'''
#import naoutil.naoenv as naoenv
#import naoutil.memory as memory
from community.core import Agent
#from naoutil.broker import Broker
#from fluentnao.nao import Nao
from community.statechart import EventFSMBehaviour
from community.behaviours.executor import TaskExecutor
from community.behaviours.system import SystemCore
from nao.behaviours.communication import Communicator
from time import sleep
#import qi
from threading import Lock


class NaoAgent(Agent):

    def __init__(self, name, host, secret, selfIP):
        #self.naoqiInit(selfIP)
        behaviours = [SystemCore(), TaskExecutor(), self.createEventFSMBehaviour(), Communicator()]
        Agent.__init__(self, name, host, secret, behaviours, [])

    EVENT_ORDER_LISTEN = "EVENT_ORDER_LISTEN"
    EVENT_ORDER_SIT_DOWN = "EVENT_ORDER_SIT_DOWN"
    EVENT_ORDER_STAND_UP = "EVENT_ORDER_STAND_UP"
    EVENT_ORDER_SAY_HI = "EVENT_ORDER_SAY_HI"
    EVENT_SALLE_1_RAPHAEL = "EVENT_SALLE_1_RAPHAEL"
    EVENT_SALLE_2_RAPHAEL = "EVENT_SALLE_2_RAPHAEL"
    EVENT_SALLE_3_RAPHAEL = "EVENT_SALLE_3_RAPHAEL"
    EVENT_SALLE_1_SAMIRA = "EVENT_SALLE_1_SAMIRA"
    EVENT_SALLE_2_SAMIRA = "EVENT_SALLE_2_SAMIRA"
    EVENT_SALLE_3_SAMIRA = "EVENT_SALLE_3_SAMIRA"
    EVENT_RASSEMBLEMENT = "EVENT_RASSEMBLEMENT"
    EVENT_POUSSEZ = "EVENT_POUSSEZ"
    EVENT_TURTLE_SAY = "EVENT_TURTLE_SAY"
    EVENT_MOVE = "EVENT_MOVE"

    def listenCall(myAgent, inputs, eventInputs):
        myAgent.log(inputs, "input")
        myAgent.log(eventInputs, "eventInputs")
        myAgent.log("listen Call", "LISTEN_CALL")

    def listenOrder(myAgent, inputs, eventInputs):
        myAgent.log(inputs, "input")
        myAgent.log(eventInputs, "eventInputs")
        myAgent.log("listenOrder", "LISTEN_ORDER")
        myAgent.say("J'écoute")

    def sitDown(myAgent, inputs, eventInputs):
        myAgent.log(inputs, "input")
        myAgent.log(eventInputs, "eventInputs")
        myAgent.log("sitDown", "SIT_DOWN")
        #myAgent.nao.sit()
        return 0

    def standUp(myAgent, inputs, eventInputs):
        myAgent.log(inputs, "input")
        myAgent.log(eventInputs, "eventInputs")
        myAgent.log("standUp", "STAND_UP")
        #myAgent.nao.stand()
        return 0

    def sayHi(myAgent, inputs, eventInputs):
        myAgent.log(inputs, "input")
        myAgent.log(eventInputs, "eventInputs")
        myAgent.log("sayHi", "SAY_HI")
        myAgent.sayAnimated("^start(animations/Stand/Gestures/Hey_1) Coucou ! ^wait(animations/Stand/Gestures/Hey_1)")
        return 0

    def createTurtleOrder(self, turtleName, orderName, data):
        def action(myAgent, inputs, eventInputs):
            myAgent.log(inputs, "input")
            myAgent.log(eventInputs, "eventInputs")
            myAgent.say(orderName)
        return action

    def sendGetherOrder(myAgent, inputs, eventInputs):
        myAgent.log(inputs, "input")
        myAgent.log(eventInputs, "eventInputs")
        myAgent.log("gether", "RASSEMBLEMENT")

    def sendPushOrder(myAgent, inputs, eventInputs):
        myAgent.log(inputs, "input")
        myAgent.log(eventInputs, "eventInputs")
        myAgent.log("push", "POUSSEZ")

    def onHumanMoveEvent(myAgent, inputs, eventInputs):
        myAgent.log(inputs, "input")
        myAgent.log(eventInputs, "eventInputs")
        myAgent.log("move", "onHumanMoveEvent")

    def onTurtleSayEvent(myAgent, inputs, eventInputs):
        myAgent.log(inputs, "input")
        myAgent.log(eventInputs, "eventInputs")
        myAgent.log("turtleSay", "onTurtleSayEvent")

    def naoqiInit(self, selfIP):
        speechEvents = dict()
        speechEvents["nao écoute moi"] = [NaoAgent.EVENT_ORDER_LISTEN, .37]
        speechEvents["Bonjour nao"] = [NaoAgent.EVENT_ORDER_SAY_HI, .40]
        speechEvents["Assieds-toi"] = [NaoAgent.EVENT_ORDER_SIT_DOWN, .40]
        speechEvents["Mets-toi debout"] = [NaoAgent.EVENT_ORDER_STAND_UP, .30]
        speechEvents["Raphael un"] = [NaoAgent.EVENT_SALLE_1_RAPHAEL, .27]
        speechEvents["Raphael deuxième"] = [NaoAgent.EVENT_SALLE_2_RAPHAEL, .30]
        speechEvents["Raphael troisième"] = [NaoAgent.EVENT_SALLE_3_RAPHAEL, .30]
        speechEvents["Samira un"] = [NaoAgent.EVENT_SALLE_1_SAMIRA, .27]
        speechEvents["Samira deuxième"] = [NaoAgent.EVENT_SALLE_2_SAMIRA, .30]
        speechEvents["Samira troisième"] = [NaoAgent.EVENT_SALLE_3_SAMIRA, .30]
        speechEvents["Rassemblement"] = [NaoAgent.EVENT_RASSEMBLEMENT, .35]
        speechEvents["Poussez la boite"] = [NaoAgent.EVENT_POUSSEZ, .30]

        # callbacks
        def recognitionCallback(dataName, value, message):

            d = dict(zip(value[0::2], value[1::2]))

            self.log("acquire with listening: " + str(self.isListening), "recognitionCallback")
            self.lock.acquire()
            if not self.isListening:
                self.isListening = True
                self.lock.release()
                self.log("release 1", "recognitionCallback")
                return
            self.lock.release()
            self.log("release 2", "recognitionCallback")

            for word in d:
                self.log(word + " " + str(d[word]))
                self.log("qdqdf " + word)
                if d[word] > speechEvents[word][1]:
                    self.log("1")
                    self.log(speechEvents[word][0])
                    self.raiseEvent(speechEvents[word][0])
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

            sleep(5)
            self.log("acquire 2", "animatedSpeechCallback")
            self.lock.acquire()
            self.isListening = True
            self.lock.release()
            self.log("release 2", "animatedSpeechCallback")

        def touchChangeCallback(eventName, touchInfo, subscriberIdentifier):
            for i in touchInfo:
                self.log(i)

        def rigthHandCallback(eventName, val, subscriberIdentifier):
            self.log(val)

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
            self.nao.env.speechRecognition.pause(False)
            self.nao.env.speechRecognition.setVocabulary(vocabulary, False)
        except RuntimeError as e:
            self.nao.env.speechRecognition.pause(False)
            self.log(e.message, "RuntimeError")

        self.memory.subscribeToEvent('WordRecognized', recognitionCallback)
        self.memory.subscribeToEvent('ALTextToSpeech/Status', speechCallback)
        self.memory.subscribeToEvent('ALAnimatedSpeech/EndOfAnimatedSpeech', animatedSpeechCallback)
        # self.memory.subscribeToEvent('TouchChanged', touchChangeCallback)
        # self.memory.subscribeToEvent('HandRightBackTouched', rigthHandCallback)
        # self.memory.subscribeToEvent('HandRightLeftTouched', rigthHandCallback)
        # self.memory.subscribeToEvent('HandRightRightTouched', rigthHandCallback)

    def createEventFSMBehaviour(self):

        LISTEN_CALL = "LISTEN_CALL"
        LISTEN_ORDER = "LISTEN_ORDER"
        SIT_DOWN = "SIT_DOWN"
        STAND_UP = "STAND_UP"
        SAY_HI = "SAY_HI"
        RAPHAEL_SALLE_1 = "RAPHAEL_SALLE_1"
        RAPHAEL_SALLE_2 = "RAPHAEL_SALLE_2"
        RAPHAEL_SALLE_3 = "RAPHAEL_SALLE_3"
        SAMIRA_SALLE_1 = "SAMIRA_SALLE_1"
        SAMIRA_SALLE_2 = "SAMIRA_SALLE_2"
        SAMIRA_SALLE_3 = "SAMIRA_SALLE_3"
        RASSEMBLEMENT = "RASSEMBLEMENT"
        POUSSEZ = "POUSSEZ"
        ON_MOVE_EVENT = "ON_MOVE_EVENT"
        ON_TURTLE_SAY_EVENT = "ON_TURTLE_SAY_EVENT"
        INIT = "INIT"

        def init(myAgent, inputs, eventInputs):
            self.log("init", "START_STATE")

        evfsm = EventFSMBehaviour("Liveness")

        evfsm.createState(INIT, init)
        evfsm.createState(LISTEN_CALL, NaoAgent.listenCall)
        evfsm.createState(LISTEN_ORDER, NaoAgent.listenOrder)
        evfsm.createState(SIT_DOWN, NaoAgent.sitDown)
        evfsm.createState(STAND_UP, NaoAgent.standUp)
        evfsm.createState(SAY_HI, NaoAgent.sayHi)
        evfsm.createState(RAPHAEL_SALLE_1, self.createTurtleOrder("Raphael", "goTo", "salle1"))
        evfsm.createState(RAPHAEL_SALLE_2, self.createTurtleOrder("Raphael", "goTo", "salle2"))
        evfsm.createState(RAPHAEL_SALLE_3, self.createTurtleOrder("Raphael", "goTo", "salle3"))
        evfsm.createState(SAMIRA_SALLE_1, self.createTurtleOrder("Samira", "goTo", "salle1"))
        evfsm.createState(SAMIRA_SALLE_2, self.createTurtleOrder("Samira", "goTo", "salle2"))
        evfsm.createState(SAMIRA_SALLE_3, self.createTurtleOrder("Samira", "goTo", "salle3"))
        evfsm.createState(RASSEMBLEMENT, NaoAgent.sendGetherOrder)
        evfsm.createState(POUSSEZ, NaoAgent.sendPushOrder)
        evfsm.createState(ON_MOVE_EVENT, NaoAgent.onHumanMoveEvent)
        evfsm.createState(ON_TURTLE_SAY_EVENT, NaoAgent.onTurtleSayEvent)

        evfsm.createWaitingTransition(INIT, ON_MOVE_EVENT, NaoAgent.EVENT_MOVE)
        evfsm.createWaitingTransition(INIT, ON_TURTLE_SAY_EVENT, NaoAgent.EVENT_TURTLE_SAY)
        evfsm.createWaitingTransition(INIT, LISTEN_CALL)

        evfsm.createWaitingTransition(ON_MOVE_EVENT, ON_MOVE_EVENT, NaoAgent.EVENT_MOVE)
        evfsm.createWaitingTransition(ON_TURTLE_SAY_EVENT, ON_TURTLE_SAY_EVENT, NaoAgent.EVENT_TURTLE_SAY)

        evfsm.createMultiChoiceWaitingTransition()\
            .fromState(LISTEN_CALL)\
            .ifCondition(NaoAgent.EVENT_ORDER_LISTEN).goTo(LISTEN_ORDER)\
            .elifCondition(NaoAgent.EVENT_ORDER_SAY_HI).goTo(SAY_HI) \
            .create()

        evfsm.createMultiChoiceWaitingTransition() \
            .fromState(LISTEN_ORDER) \
            .ifCondition(NaoAgent.EVENT_ORDER_SIT_DOWN).goTo(SIT_DOWN) \
            .elifCondition(NaoAgent.EVENT_ORDER_STAND_UP).goTo(STAND_UP) \
            .elifCondition(NaoAgent.EVENT_SALLE_1_RAPHAEL).goTo(RAPHAEL_SALLE_1) \
            .elifCondition(NaoAgent.EVENT_SALLE_2_RAPHAEL).goTo(RAPHAEL_SALLE_2) \
            .elifCondition(NaoAgent.EVENT_SALLE_2_RAPHAEL).goTo(RAPHAEL_SALLE_3) \
            .elifCondition(NaoAgent.EVENT_SALLE_1_SAMIRA).goTo(SAMIRA_SALLE_1) \
            .elifCondition(NaoAgent.EVENT_SALLE_2_SAMIRA).goTo(SAMIRA_SALLE_2) \
            .elifCondition(NaoAgent.EVENT_SALLE_2_SAMIRA).goTo(SAMIRA_SALLE_3) \
            .elifCondition(NaoAgent.EVENT_RASSEMBLEMENT).goTo(RASSEMBLEMENT) \
            .elifCondition(NaoAgent.EVENT_POUSSEZ).goTo(POUSSEZ) \
            .create()

        evfsm.createSimpleTransition(SIT_DOWN, LISTEN_CALL, 0)
        evfsm.createSimpleTransition(STAND_UP, LISTEN_CALL, 0)
        evfsm.createSimpleTransition(SAY_HI, LISTEN_CALL, 0)
        evfsm.createSimpleTransition(RAPHAEL_SALLE_1, LISTEN_CALL, 0)
        evfsm.createSimpleTransition(RAPHAEL_SALLE_2, LISTEN_CALL, 0)
        evfsm.createSimpleTransition(RAPHAEL_SALLE_3, LISTEN_CALL, 0)
        evfsm.createSimpleTransition(SAMIRA_SALLE_1, LISTEN_CALL, 0)
        evfsm.createSimpleTransition(SAMIRA_SALLE_2, LISTEN_CALL, 0)
        evfsm.createSimpleTransition(SAMIRA_SALLE_3, LISTEN_CALL, 0)
        evfsm.createSimpleTransition(RASSEMBLEMENT, LISTEN_CALL, 0)
        evfsm.createSimpleTransition(POUSSEZ, LISTEN_CALL, 0)

        evfsm.setStartingPoint(INIT)

        return evfsm

    def log(self, msg, module=""):
        #qi.logInfo(module, msg)
        print module, ":", msg

    def say(self, text):
        #self.isAnimatedSay = False
        self.log(text)
        #self.nao.say(text)

    def sayAnimated(self, text):
        #self.isAnimatedSay = True
        self.log(text)
        #self.nao.animate_say(text)

    def takeDown(self):
        print "TakeDown"
        #self.memory.unsubscribeToEvent('WordRecognized')
        #self.memory.unsubscribeToEvent('ALTextToSpeech/Status')
        #self.memory.unsubscribeToEvent('ALAnimatedSpeech/EndOfAnimatedSpeech')
        # self.memory.unsubscribeToEvent('TouchChanged')
        # self.memory.unsubscribeToEvent('HandRightBackTouched')
        # self.memory.unsubscribeToEvent('HandRightLeftTouched')
        # self.memory.unsubscribeToEvent('HandRightRightTouched')
        #self.broker.shutdown()
