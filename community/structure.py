


class Task:
    def run(self):
        raise NotImplementedError


class BeliefListener:
    def __init__(self):
        pass

    def onBeliefChanged(self, sentence):
        raise NotImplementedError

