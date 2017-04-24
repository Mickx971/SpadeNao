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

    def __init__(self, name, host, secret, behaviours):
        super(Agent, self).__init__(name + "@" + host, secret)
        self.localName = name
        self.host = host
        self.name = self.localName + "@" + self.host
        self.behaviours = dict()
        for behaviour in behaviours:
            self.behaviours[behaviour.getName()] = behaviour

    def _setup(self):
        for behaviour in self.behaviours.itervalues():
            if behaviour.haveOntology():
                template = spade.Behaviour.ACLTemplate()
                template.setOntology(behaviour.getOntology())
                self.addBehaviour(behaviour, spade.Behaviour.MessageTemplate(template))
            else:
                self.addBehaviour(behaviour)