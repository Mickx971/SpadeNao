from collections import defaultdict
from community.core import Behaviour
from community.structure import Task
from community.structure import BeliefListener


class State(Task):
    def __init__(self, stateChart, name, action, sync=False):
        self.stateChart = stateChart
        self.name = name
        self.action = action
        self.sync = sync
        self.syncCounter = 0

    def getName(self):
        return self.name

    def isSyncState(self):
        return self.sync

    def addSyncCounter(self):
        self.syncCounter = self.syncCounter + 1

    def getSyncCounter(self):
        return self.syncCounter

    def run(self):
        self.action()
        self.stateChart.onActionPerformed(self)


class Transition:

    class Status:
        WAITING = 0
        RUNNING = 1
        FINISHED = 2

    def __init__(self, inState=None, outState=None, condition=None):
        self.inState = inState
        self.outState = outState
        self.condition = condition

    def setInState(self, state):
        self.inState = state

    def setOutState(self, state):
        self.outState = state

    def setCondition(self, condition):
        self.condition = condition

    def isWellFormed(self):
        return self.inState is not None and self.outState is not None


class MultiChoiceTransition:
    def __init__(self):
        self.inState = None
        self.transitions = list()

    def setInState(self, inState):
        self.inState = inState

    def addChoice(self, transition):
        transition.setInState(self.inState)
        self.transitions.append(transition)

    def isWellFormed(self):
        if self.inState is None or len(self.transitions) == 0:
            return False
        for i in range(0, len(self.transitions)):
            if not self.transitions[i].isWellFormed():
                return False
            elif self.transitions[i].condition is None:
                if len(self.transitions) == 1 or i < len(self.transitions) - 1:
                    return False
        return True


class TransitionStatus:
    def __init__(self):
        self.status = Transition.Status.WAITING

    def isDone(self):
        return self.status == Transition.Status.FINISHED

    def done(self):
        self.status = Transition.Status.FINISHED

    def setRunning(self):
        self.status = Transition.Status.RUNNING

    def isWaiting(self):
        return self.status == Transition.Status.WAITING


class TransitionInstance(TransitionStatus):
    def __init__(self, transition):
        TransitionStatus.__init__(self)
        self.transition = transition

    def getCondition(self):
        return self.transition.condition

    def getInState(self):
        return self.transition.inState

    def getOutState(self):
        return self.transition.outState

    def isMultiChoiceTransition(self):
        return False


class MultiChoiceTransitionInstance(TransitionStatus):
    def __init__(self, multiChoiceTransition):
        TransitionStatus.__init__(self)
        self.multiChoiceTransition = multiChoiceTransition

    def getChoices(self):
        return self.multiChoiceTransition.transitions

    def isMultiChoiceTransition(self):
        return True


class MultiChoiceTransitionBuilder:

    class MultiChoiceConditionBuilder:
        def __init__(self, multiChoice, sentence=None):
            self.multiChoice = multiChoice
            self.transition = Transition()
            self.transition.setCondition(sentence)

        def goTo(self, outStateName):
            outState = self.multiChoice.stateChart.states[outStateName]
            self.transition.setOutState(outState)
            if outState.isSyncState():
                outState.addSyncCounter()
            return self.multiChoice

    def __init__(self, stateChart):
        self.stateChart = stateChart
        self.ifDone = False
        self.elseDone = False
        self.inStateSetted = False
        self.multiChoiceTransition = MultiChoiceTransition()

    def fromState(self, name):
        if not self.inStateSetted:
            self.inStateSetted = True
            self.multiChoiceTransition.setInState(self.stateChart.states[name])
            return self
        else:
            raise RuntimeError("fromState already setted")

    def ifCondition(self, sentence):
        if not self.ifDone :
            self.ifDone = True
            builder = self.MultiChoiceConditionBuilder(self, sentence)
            self.multiChoiceTransition.addChoice(builder.transition)
            return builder
        else:
            raise RuntimeError("IfCondition already called")

    def elifCondition(self, sentence):
        if self.ifDone and not self.elseDone:
            builder = self.MultiChoiceConditionBuilder(self, sentence)
            self.multiChoiceTransition.addChoice(builder.transition)
            return builder
        else:
            raise RuntimeError("IfCondition not yet called")

    def elseCondition(self):
        if self.ifDone and not self.elseDone:
            self.elseDone = True
            builder = self.MultiChoiceConditionBuilder(self)
            self.multiChoiceTransition.addChoice(builder.transition)
            return builder
        else:
            raise RuntimeError("IfCondition not yet called")

    def create(self):
        if self.multiChoiceTransition.isWellFormed():
            self.stateChart.addMultiChoiceTransition(self.multiChoiceTransition)
        else:
            raise RuntimeError("Fail to create MultiChoiceTransition")


class StateChart(Behaviour, BeliefListener):
    def __init__(self, name):
        super(StateChart, self).__init__(name)
        self.states = dict()
        self.startState = None
        self.transitions = defaultdict(list)
        self.waitingTransitions = list()
        self.started = False

    def onStart(self):
        print "Liveness statechart started"
        self.myAgent.addBeliefListener(self)

    def onEnd(self):
        self.myAgent.removeBeliefListener(self)

    def createState(self, name, action, sync=False):
        state = State(self, name, action, sync)
        self.states[name] = state

    def createsSyncState(self, name, action):
        self.createState(name, action, True)

    def setStartingPoint(self, stateName):
        self.startState = self.states[stateName]

    def createTransition(self, fromStateName, toStateName, conditionSentence=None):
        s1 = self.states[fromStateName]
        s2 = self.states[toStateName]
        self.transitions[s1].append(Transition(s1, s2, conditionSentence))
        if s2.isSyncState():
            s2.addSyncCounter()

    def createMultiChoiceTransition(self):
        return MultiChoiceTransitionBuilder(self)

    def addMultiChoiceTransition(self, multiChoiceTransition):
        self.transitions[multiChoiceTransition.inState].append(multiChoiceTransition)

    def onActionPerformed(self, state):
        for transition in self.transitions[state]:
            if isinstance(transition, Transition):
                self.performParallelTransition(transition)
            elif isinstance(transition, MultiChoiceTransition):
                self.performMultiChoiceTransition(transition)
            else:
                raise Exception("Unknown transition type")

    def performParallelTransition(self, transition):
        if transition.condition is None or self.myAgent.askBelieve(transition.condition):
            self.executeState(transition.outState)
        else:
            self.waitingTransitions.append(TransitionInstance(transition))

    def performMultiChoiceTransition(self, multiChoice):
        for choice in multiChoice.transitions:
            if choice.condition is None or self.myAgent.askBelieve(choice.condition):
                self.executeState(choice.outState)
                break
        else:
            self.waitingTransitions.append(MultiChoiceTransitionInstance(multiChoice))

    def executeState(self, state):
        self.myAgent.getTaskExecutor().addTask(state)

    def onBeliefChanged(self, sentence):
        for transition in self.waitingTransitions:
            if transition.isWaiting():
                if transition.isMultiChoiceTransition():
                    self.tryToExecuteMultiChoiceTransition(transition)
                else:
                    self.tryToExecuteTransition(transition)

        self.waitingTransitions = [t for t in self.waitingTransitions if not t.isDone()]

    def tryToExecuteTransition(self, transition):
        if self.myAgent.askBelieve(transition.getCondition()) is True:
            transition.setRunning()
            self.executeState(transition.getOutState())

    def tryToExecuteMultiChoiceTransition(self, multiChoiceTransition):
        for choice in multiChoiceTransition.getChoices():
            if choice.condition is None or self.myAgent.askBelieve(choice.condition):
                multiChoiceTransition.setRunning()
                self.executeState(choice.outState)
                break

    def process(self):
        if not self.started:
            self.started = True
            self.executeState(self.startState)
