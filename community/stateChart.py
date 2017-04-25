from collections import defaultdict
from community.core import Behaviour


class Task:
    def run(self):
        raise NotImplementedError


class State(Task):
    def __init__(self, stateChart, name, action):
        self.stateChart = stateChart
        self.name = name
        self.action = action

    def getName(self):
        return self.name

    def run(self):
        self.action()
        self.stateChart.onActionPerformed(self)


class Transition:

    class State:
        WAITING = 0
        RUNNING = 1
        FINISHED = 2

    def __init__(self, inState, outState, condition):
        self.inState = inState
        self.outState = outState
        self.condition = condition


class TransitionInstance:
    def __init__(self, transition):
        self.transition = transition
        self.status = Transition.State.WAITING

    def isDone(self):
        return self.status == Transition.State.FINISHED

    def done(self):
        self.status = Transition.State.FINISHED

    def setRunning(self):
        self.status = Transition.State.RUNNING

    def isWaiting(self):
        return self.status == Transition.State.WAITING

    def getCondition(self):
        return self.transition.condition

    def getInState(self):
        return self.transition.inState

    def getOutState(self):
        return self.transition.outState


class BeliefListener:
    def onBeliefChanged(self, sentence):
        raise NotImplementedError


class StateChart(Behaviour, BeliefListener):
    def __init__(self, name):
        super(StateChart, self).__init__(name)
        self.states = dict()
        self.start = None
        self.transitions = defaultdict(list)
        self.waitingTransitions = list()

    def onStart(self):
        self.myAgent.addBeliefListener(self)

    def onEnd(self):
        self.myAgent.removeBeliefListener(self)

    def createState(self, name, action):
        state = State(name, action)
        self.states[name] = state

    def setStartingPoint(self, stateName):
        self.start = self.states[stateName]

    def createTransition(self, fromStateName, toStateName, conditionSentence=None):
        s1 = self.states[fromStateName]
        s2 = self.states[toStateName]
        self.transitions[s1].append(Transition(s1, s2, conditionSentence))

    def onActionPerformed(self, state):
        for transition in self.transitions[state]:
            if transition.condition is None:
                self.executeState(transition.outState)
            else:
                self.prepareTransition(TransitionInstance(transition))

    def prepareTransition(self, transition):
        if self.myAgent.askBelieve(transition.getCondition()) is True:
            self.executeState(transition.getOutState())
        else:
            self.waitingTransitions.append(transition)

    def executeState(self, state):
        self.myAgent.getTaskExecutor().addTask(state)

    def onBeliefChanged(self, sentence):
        for transition in self.waitingTransitions:
            if transition.isWaiting() and self.myAgent.askBelieve(transition.getCondition()) is True:
                transition.setRunning()
                self.executeState(transition.getOutState())

        self.waitingTransitions = [t for t in self.waitingTransitions if not t.isDone()]


if __name__ == "__main__":

    def printCoucou():
        print "coucou"

    def printBonjour():
        print "bonjour"

    st = StateChart()
    st.createState("first", printCoucou)
    st.createState("second", printBonjour)
    st.createTransition("first", "second", "move(nao1,)")
    st.setStartingPoint("first")
