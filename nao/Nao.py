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
from nao.behaviours.communication import Communicator
from time import sleep
import qi
from threading import Lock
import json
from collections import defaultdict


class NaoAgent(Agent):

    def __init__(self, name, host, secret, selfIP):
        self.naoqiInit(selfIP)
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
    EVENT_TURTLE_MOVE = "EVENT_TURTLE_MOVE"
    EVENT_TURTLE_PUSH = "EVENT_TURTLE_PUSH"
    EVENT_MOVE = "EVENT_MOVE"

    def listenCall(myAgent, inputs, eventInputs):
        myAgent.log("listen Call", "LISTEN_CALL")

    def listenOrder(myAgent, inputs, eventInputs):
        myAgent.log("listenOrder", "LISTEN_ORDER")
        myAgent.say("i am listening")

    def sitDown(myAgent, inputs, eventInputs):
        myAgent.log("sitDown", "SIT_DOWN")
        myAgent.nao.sit()
        return 0

    def standUp(myAgent, inputs, eventInputs):
        myAgent.log("standUp", "STAND_UP")
        myAgent.nao.stand()
        return 0

    def sayHi(myAgent, inputs, eventInputs):
        myAgent.log("sayHi", "SAY_HI")
        myAgent.sayAnimated("^start(animations/Stand/Gestures/Hey_1) Hello ! ^wait(animations/Stand/Gestures/Hey_1)")
        return 0

    def createTurtleOrder(self, turtleName, orderName, data):

        def action(myAgent, inputs, eventInputs):
            myAgent.say(turtleName + " go to " + self.destinationSpeech[data])
            myAgent.behaviours["Communicator"].sendMoveOrder(turtleName, data)
            return 0

        return action

    def sendGetherOrder(myAgent, inputs, eventInputs):
        myAgent.log("send gether order", "OnGetherOrder")
        communicator = myAgent.behaviours["Communicator"]
        myAgent.say("")
        communicator.sendGetherOrder()
        return 0

    def sendPushOrder(myAgent, inputs, eventInputs):
        myAgent.log("send push order", "OnPushOrder")
        communicator = myAgent.behaviours["Communicator"]
        myAgent.say("Tortues poussez la boite!")
        communicator.sendPushOrder()
        return 0

    def onHumanMoveEvent(myAgent, inputs, eventInputs):
        msg = eventInputs[0]
        content = msg.getContent().replace("\\\"", '"')
        content = myAgent.parseAclMessageContent(content, True)
        myAgent.log(content, "OnHumanMoveEvent")
        myAgent.say("La caméra indique un changement.")

        pourcentage = int(float(content["prob"]) * 100)

        speechBegin = "Elle détecte "
        speechEnd = " avec une fiabilité de " + str(pourcentage) + " pourcent."

        if content["action"] == "detect_faces":
            if content["nbFaces"] == 0:
                myAgent.say("Elle ne détecte personne")
            elif content["nbFaces"] == 1:
                if content["nbMale"] == 1:
                    myAgent.say("un homme " + speechEnd)
                else:
                    myAgent.say("une femme " + speechEnd)
            else:
                speech = speechBegin + str(content["nbFaces"]) + " personnes dont " + str(content["nbMale"]) + " hommes et " + str(content["nbFemale"]) + " femmes" + str(speechEnd)
                myAgent.say(speech)
        else:
            print content["classes"]
            if len(content["classes"]) > 0:
                speech = speechBegin + " les choses suivantes: " + ", ".join(content["classes"])
            else:
                speech = "Elle ne détecte rien du tout"
            myAgent.say(speech)

    def onTurtleMoveEvent(myAgent, inputs, eventInputs):
        myAgent.log(str(eventInputs[0]), "OnTurtleMoveEvent")

        msg = eventInputs[0]
        communicator = myAgent.behaviours["Communicator"]

        senderName = communicator.getSenderName(msg.getSender())
        content = myAgent.parseAclMessageContent(msg)
        actionName = content["action"]
        status = content["status"]

        if status == "succeeded":
            speech = " has succeeded to go "
        else:
            speech = " has failed to go "

        if actionName == "goNear":
            speech = senderName + speech + " Near " + communicator.getOtherTurtleName(senderName)
        else:
            speech = senderName + speech + " to " + myAgent.destinationSpeech[actionName]

        myAgent.say(speech)

    def onTurtlePushEvent(myAgent, inputs, eventInputs):
        myAgent.log("", "onTurtlePushEvent")

        msg = eventInputs[0]
        content = myAgent.parseAclMessageContent(msg)
        status = content["status"]

        if status != "succeeded":
            speech = "Les tortues n'ont pas réussi à pousser la boîte"
        else:
            speech = "Les tortues ont réussi à pousser la boîte"

        myAgent.say(speech)

    def naoqiInit(self, selfIP):
        speechEvents = dict()
        speechEvents["nao listen to me"] = [NaoAgent.EVENT_ORDER_LISTEN, .37]
        speechEvents["Hello nao"] = [NaoAgent.EVENT_ORDER_SAY_HI, .40]
        speechEvents["sit down"] = [NaoAgent.EVENT_ORDER_SIT_DOWN, .40]
        speechEvents["Stand up"] = [NaoAgent.EVENT_ORDER_STAND_UP, .30]
        speechEvents["Tell Raphael to go to the room number 1"] = [NaoAgent.EVENT_SALLE_1_RAPHAEL, .27]
        speechEvents["Tell Raphael to go to the room number 2"] = [NaoAgent.EVENT_SALLE_2_RAPHAEL, .30]
        speechEvents["Tell Raphael to go to the room number 3"] = [NaoAgent.EVENT_SALLE_3_RAPHAEL, .30]
        speechEvents["Tell Samira to go to the room number 1"] = [NaoAgent.EVENT_SALLE_1_SAMIRA, .27]
        speechEvents["Tell Samira to go to the room number 2"] = [NaoAgent.EVENT_SALLE_2_SAMIRA, .30]
        speechEvents["Tell Samira to go to the room number 3"] = [NaoAgent.EVENT_SALLE_3_SAMIRA, .30]
        speechEvents["Tell one turtle to go near the other"] = [NaoAgent.EVENT_RASSEMBLEMENT, .35]
        #speechEvents["Poussez la boite"] = [NaoAgent.EVENT_POUSSEZ, .30]

        # callbacks
        def recognitionCallback(dataName, value, message):

            d = dict(zip(value[0::2], value[1::2]))

            self.lock.acquire()
            if not self.isListening:
                self.isListening = True
                self.lock.release()
                return
            self.lock.release()

            for word in d:
                self.log(word + " " + str(d[word]))
                if d[word] > speechEvents[word][1]:
                    self.log(speechEvents[word][0])
                    self.raiseEvent(speechEvents[word][0])
                    return

            self.say("I did not understand")

        def speechCallback(eventName, value, subscriberIdentifier):
            if value[1] in ["thrown", "stopped", "done"] and not self.isAnimatedSay:
                self.lock.acquire()
                self.isListening = False
                self.lock.release()

                sleep(2)
                self.lock.acquire()
                self.isListening = True
                self.lock.release()

        def animatedSpeechCallback(eventName, taskId, subscriberIdentifier):
            self.lock.acquire()
            self.isListening = False
            self.lock.release()

            sleep(5)
            self.lock.acquire()
            self.isListening = True
            self.lock.release()

        def touchChangeCallback(eventName, touchInfo, subscriberIdentifier):
            for i in touchInfo:
                self.log(i)

        def rigthHandCallback(eventName, val, subscriberIdentifier):
            self.log(val)

        self.ip = selfIP
        self.broker = Broker('bootstrapBroker', naoIp=self.ip, naoPort=9559)

        # FluentNao
        self.nao = Nao(naoenv.make_environment(None))
        #self.nao.env.tts.setLanguage(language)
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

        self.destinationSpeech = dict()
        self.destinationSpeech["salle1"] = "the room 1"
        self.destinationSpeech["salle2"] = "the room 2"
        self.destinationSpeech["salle3"] = "the room 3"
        self.destinationSpeech["principale"] = "the principal room"

        self.cameraEventSpeech = defaultdict(lambda : "")
        self.cameraEventSpeech["moveIn"] = "La camera m'indique que quelqu'un est entré dans l'espace"
        self.cameraEventSpeech["moveOut"] = "La camera m'indique que quelqu'un est sortie de l'espace"

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
        ON_TURTLE_MOVE_EVENT = "ON_TURTLE_MOVE_EVENT"
        ON_TURTLE_PUSH_EVENT = "ON_TURTLE_PUSH_EVENT"
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
        evfsm.createState(RAPHAEL_SALLE_1, self.createTurtleOrder("raphael", "goTo", "salle1"))
        evfsm.createState(RAPHAEL_SALLE_2, self.createTurtleOrder("raphael", "goTo", "salle2"))
        evfsm.createState(RAPHAEL_SALLE_3, self.createTurtleOrder("raphael", "goTo", "salle3"))
        evfsm.createState(SAMIRA_SALLE_1, self.createTurtleOrder("samira", "goTo", "salle1"))
        evfsm.createState(SAMIRA_SALLE_2, self.createTurtleOrder("samira", "goTo", "salle2"))
        evfsm.createState(SAMIRA_SALLE_3, self.createTurtleOrder("samira", "goTo", "salle3"))
        evfsm.createState(RASSEMBLEMENT, NaoAgent.sendGetherOrder)
        evfsm.createState(POUSSEZ, NaoAgent.sendPushOrder)
        evfsm.createState(ON_MOVE_EVENT, NaoAgent.onHumanMoveEvent)
        evfsm.createState(ON_TURTLE_MOVE_EVENT, NaoAgent.onTurtleMoveEvent)
        evfsm.createState(ON_TURTLE_PUSH_EVENT, NaoAgent.onTurtlePushEvent)

        evfsm.createWaitingTransition(INIT, ON_MOVE_EVENT, NaoAgent.EVENT_MOVE)
        evfsm.createWaitingTransition(INIT, ON_TURTLE_MOVE_EVENT, NaoAgent.EVENT_TURTLE_MOVE)
        evfsm.createWaitingTransition(INIT, ON_TURTLE_PUSH_EVENT, NaoAgent.EVENT_TURTLE_PUSH)
        evfsm.createWaitingTransition(INIT, LISTEN_CALL)

        evfsm.createWaitingTransition(ON_MOVE_EVENT, ON_MOVE_EVENT, NaoAgent.EVENT_MOVE)
        evfsm.createWaitingTransition(ON_TURTLE_MOVE_EVENT, ON_TURTLE_MOVE_EVENT, NaoAgent.EVENT_TURTLE_MOVE)
        evfsm.createWaitingTransition(ON_TURTLE_PUSH_EVENT, ON_TURTLE_PUSH_EVENT, NaoAgent.EVENT_TURTLE_PUSH)

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
            .elifCondition(NaoAgent.EVENT_SALLE_3_RAPHAEL).goTo(RAPHAEL_SALLE_3) \
            .elifCondition(NaoAgent.EVENT_SALLE_1_SAMIRA).goTo(SAMIRA_SALLE_1) \
            .elifCondition(NaoAgent.EVENT_SALLE_2_SAMIRA).goTo(SAMIRA_SALLE_2) \
            .elifCondition(NaoAgent.EVENT_SALLE_3_SAMIRA).goTo(SAMIRA_SALLE_3) \
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
        qi.logInfo(module, msg)
        #print module, ":", msg

    def say(self, text):
        self.isAnimatedSay = False
        self.log(text, "Say")
        self.nao.say(text)

    def sayAnimated(self, text):
        self.isAnimatedSay = True
        self.log(text, "Say")
        self.nao.animate_say(text)

    def parseAclMessageContent(self, aclMessage, isString=False):
        def ascii_encode_dict(data):
            if isinstance(data, dict):
                return dict(map(ascii_encode_dict, pair) for pair in data.items())
            elif isinstance(data, list):
                return [ascii_encode_dict(e) for e in data]
            elif isinstance(data, unicode):
                return data.encode('ascii')
            else:
                return data

        try:
            if not isString :
                return json.loads(aclMessage.getContent(), object_hook=ascii_encode_dict)
            return json.loads(aclMessage, object_hook=ascii_encode_dict)
        except Exception as e:
            self.log(e.message, "Error: ")
            return None

    def takeDown(self):
        print "TakeDown"
        self.memory.unsubscribeToEvent('WordRecognized')
        self.memory.unsubscribeToEvent('ALTextToSpeech/Status')
        self.memory.unsubscribeToEvent('ALAnimatedSpeech/EndOfAnimatedSpeech')
        # self.memory.unsubscribeToEvent('TouchChanged')
        # self.memory.unsubscribeToEvent('HandRightBackTouched')
        # self.memory.unsubscribeToEvent('HandRightLeftTouched')
        # self.memory.unsubscribeToEvent('HandRightRightTouched')
        self.broker.shutdown()
