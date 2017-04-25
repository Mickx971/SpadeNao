import spade


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

    def _process(self):
        pass


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

    def _onTick(self):
        pass


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

    def _process(self):
        pass

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

    def _process(self):
        pass


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


class Agent(spade.Agent.Agent):

    def __init__(self, name, host, secret, behaviours, initKB):
        super(Agent, self).__init__(name + "@" + host, secret)
        self.localName = name
        self.host = host
        self.name = self.localName + "@" + self.host
        self.behaviours = dict()
        self.initKB = initKB
        self.kbClosed = True
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
            self.addBelieve(fact)

    def _setup(self):
        self.initBehaviours()
        self.initKnowledgeBase()

    def askBelieve(self, sentence):
        try:
            return super(Agent, self).askBelieve(sentence)
        except Exception as e:
            print "Unexpected error:", type(e)
            print e
            return False

    def takeDown(self):
        if not self.kbClosed:
            self.kbClosed = True
            try:
                self.kb.ask("halt.")
            except:
                pass
