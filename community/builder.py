from community.core import Agent
from community.behaviours.system import SystemCore


class AgentBuilder:
    @staticmethod
    def constructAgent(name, platformName, secret, behaviors):
        behaviors.add(SystemCore())
        return Agent(name, platformName, secret, behaviors)

