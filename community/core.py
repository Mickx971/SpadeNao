import spade
import traceback
from collections import defaultdict


class Behaviour(spade.Behaviour.Behaviour):
    def __init__(self, name, ontology=None):
        super(Behaviour, self).__init__()
        self.name = name
        self.ontology = ontology

    def haveOntology(self):
        return self.ontology is not None

    def getOntology(self):
        return self.ontology

    def getName(self):
        return self.name

    def process(self):
        pass

    def _process(self):
        try:
            self.process()
        except:
            traceback.print_exc()


class PeriodicBehaviour(spade.Behaviour.PeriodicBehaviour):
    def __init__(self, name, period, ontology=None):
        super(PeriodicBehaviour, self).__init__(period)
        self.name = name
        self.ontology = ontology

    def haveOntology(self):
        return self.ontology is not None

    def getOntology(self):
        return self.ontology

    def getName(self):
        return self.name

    def onTick(self):
        pass

    def _onTick(self):
        try:
            self.onTick()
        except:
            traceback.print_exc()


class OneShotBehaviour(spade.Behaviour.OneShotBehaviour):
    def __init__(self, name, ontology=None):
        super(OneShotBehaviour, self).__init__()
        self.name = name
        self.ontology = ontology

    def haveOntology(self):
        return self.ontology is not None

    def getOntology(self):
        return self.ontology

    def getName(self):
        return self.name

    def process(self):
        pass

    def _process(self):
        try:
            self.process()
        except:
            traceback.print_exc()


class EventBehaviour(spade.Behaviour.EventBehaviour):
    def __init__(self, name, ontology=None):
        super(EventBehaviour, self).__init__()
        self.name = name
        self.ontology = ontology

    def haveOntology(self):
        return self.ontology is not None

    def getOntology(self):
        return self.ontology

    def getName(self):
        return self.name

    def process(self):
        pass

    def _process(self):
        try:
            self.process()
        except:
            traceback.print_exc()


class FSMBehaviour(spade.Behaviour.FSMBehaviour):
    def __init__(self, name, ontology=None):
        super(FSMBehaviour, self).__init__()
        self.name = name
        self.ontology = ontology

    def haveOntology(self):
        return self.ontology is not None

    def getOntology(self):
        return self.ontology

    def getName(self):
        return self.name

    def process(self):
        pass

    def _process(self):
        try:
            self.process()
        except:
            traceback.print_exc()


class Agent(spade.Agent.Agent):

    def __init__(self, name, host, secret, behaviours, initKB):
        super(Agent, self).__init__(name + "@" + host, secret)
        self.localName = name
        self.host = host
        self.name = self.localName + "@" + self.host
        self.behaviours = dict()
        self.initKB = initKB
        self.kbClosed = True
        self.beliefListeners = set()
        self.eventListeners = set()
        self.data = defaultdict(lambda: None)
        self.believes = defaultdict(lambda: False)
        for behaviour in behaviours:
            self.behaviours[behaviour.getName()] = behaviour

    def initBehaviours(self):
        for behaviour in self.behaviours.itervalues():
            if behaviour.haveOntology():
                template = spade.Behaviour.ACLTemplate()
                template.setOntology(behaviour.getOntology())
                self.addBehaviour(behaviour, spade.Behaviour.MessageTemplate(template))
            else:
                self.addBehaviour(behaviour)

    def initKnowledgeBase(self):
        for fact in self.initKB:
            print "add fact: ", fact
            self.addBelieve(fact)

    def _setup(self):
        try:
            self.initKnowledgeBase()
            self.initBehaviours()
        except:
            traceback.print_exc()

    def addBeliefListener(self, listener):
        self.beliefListeners.add(listener)

    def removeBeliefListener(self, listener):
        if listener in self.beliefListeners:
            self.beliefListeners.remove(listener)

    def addEventListener(self, listener):
        self.eventListeners.add(listener)

    def removeEventListener(self, listener):
        if listener in self.eventListeners:
            self.eventListeners.remove(listener)

    def askBelieve(self, sentence):
        return self.believes[sentence]

    def removeBelieve(self, sentence, type="delete"):
        self.believes.pop(sentence, None)

    def addBelieve(self, sentence, typeAction="insert"):
        self.believes[sentence] = True
        for listener in self.beliefListeners:
            listener.onBeliefChanged(sentence)

    def raiseEvent(self, event):
        for listener in self.eventListeners:
            listener.onEvent(event)

    def setData(self, key, value):
        self.data[key] = value

    def getData(self, key):
        return self.data[key]

    def getTaskExecutor(self):
        executor = "TaskExecutor"
        if executor in self.behaviours:
            return self.behaviours[executor]
        else:
            print "Error: No TaskExecutor behaviour found in agent"
