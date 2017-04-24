from community.core import Agent
from community.behaviours.system import SystemCore


class AgentBuilder:
    def __init__(self):
        self.name = None
        self.secret = None
        self.platform = None
        self.behaviours = []
        self.facts = []

    def reset(self):
        self.name = None
        self.secret = None
        self.platform = None
        self.behaviours = []
        self.facts = []

    def setName(self, name):
        self.name = name
        return self

    def setPlatform(self, platform):
        self.platform = platform
        return self

    def setSecret(self, secret):
        self.secret = secret
        return self

    def addBehaviour(self, behaviour):
        self.behaviours.append(behaviour)
        return self

    def addFact(self, fact):
        self.facts.append(fact)
        return self

    def create(self):
        if len(self.behaviours) == 0 or self.name is None or self.platform is None or self.secret is None:
            raise RuntimeError("Wrong agent instanciation")
        self.behaviours.append(SystemCore())
        agent = Agent(self.name, self.platform, self.secret, self.behaviours, self.facts)
        self.reset()
        return agent
