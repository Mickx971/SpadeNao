import spade
import traceback


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

    def done(self):
        return True


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
        self.beliefListener = dict()
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
        self.kbClosed = False
        self.configureKB("SWI", None, "swipl")
        self.kb.ask("set_prolog_flag(unknown, fail)")
        for fact in self.initKB:
            print "add fact: ", fact
            self.addBelieve(fact)
        #Very important: initialize swipl connection
        self.askBelieve("true")
        print "Database opened"

    def _setup(self):
        try:
            self.initKnowledgeBase()
            self.initBehaviours()
        except:
            traceback.print_exc()

    def addBeliefListener(self, listener):
        self.beliefListener[listener] = listener

    def removeBeliefListener(self, listener):
        self.beliefListener.pop(listener, None)

    def askBelieve(self, sentence):
        return super(Agent, self).askBelieve(sentence)

    def addBelieve(self, sentence, typeAction="insert"):
        super(Agent, self).addBelieve(sentence, typeAction)
        for listener in self.beliefListener.itervalues():
            listener.onBeliefChanged(sentence)

    def takeDown(self):
        if not self.kbClosed:
            self.kbClosed = True
            try:
                self.kb.ask("halt.")
                print "Database closed"
            except:
                pass

    def getTaskExecutor(self):
        executor = "TaskExecutor"
        if executor in self.behaviours:
            return self.behaviours[executor]
        else:
            print "Error: No TaskExecutor behaviour found in agent"
