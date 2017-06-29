from collections import defaultdict
from community.core import OneShotBehaviour
from community.structure import Task
from community.structure import *
from time import sleep
import traceback


class State:
    def __init__(self, name, action, sync=False):
        self.name = name
        self.action = action
        self.sync = sync
        self.syncCounter = 0 if sync else 1

    def getName(self):
        return self.name

    def isSyncState(self):
        return self.sync

    def addSyncCounter(self):
        self.syncCounter = self.syncCounter + 1

    def getSyncCounter(self):
        return self.syncCounter


class StateInstance(Task):
    def __init__(self, stateChart, state, callback):
        self.stateChart = stateChart
        self.state = state
        self.syncCounter = 1
        self.callback = callback
        self.inputs = list()
        self.eventInputs = list()

    def addInput(self, input):
        self.inputs.append(input)

    def addEventInput(self, event):
        self.eventInputs.append(event)

    def run(self):
        if self.syncCounter == self.state.syncCounter:
            res = None
            try:
                res = self.state.action(self.stateChart.myAgent, self.inputs, self.eventInputs)
            except:
                traceback.print_exc()
            self.callback(self, res)
        else:
            self.syncCounter = self.syncCounter + 1

    def getState(self):
        return self.state


class Transition:

    class Status:
        WAITING = 0
        RUNNING = 1
        FINISHED = 2

    def __init__(self, inState=None, outState=None, condition=None):
        self.inState = inState
        self.outState = outState
        self.condition = None
        self.event = None
        if condition is not None:
            self.setCondition(condition)

    def setInState(self, state):
        self.inState = state

    def setOutState(self, state):
        self.outState = state

    def setCondition(self, condition):
        self.condition = ""
        for word in condition.split(","):
            if word.startswith("EVENT"):
                self.event = word
            else:
                self.condition += "," + word
        if self.condition == "":
            self.condition = None
        else:
            self.condition = self.condition[1:]

    def isWellFormed(self):
        return self.inState is not None and self.outState is not None

    def printTransition(self):
        print self.inState.getName(), self.outState.getName(), self.event, self.condition


def TransitionCondition(*conditions):
    if len([c for c in conditions if c.startswith == "EVENT"]):
        raise RuntimeError("Condition can have only one event")
    s = ","
    return s.join(conditions)


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
            elif self.transitions[i].condition is None and self.transitions[i].event is None:
                if len(self.transitions) == 1 or i < len(self.transitions) - 1:
                    return False
        return True

    def getOutStates(self):
        outStates = list()
        for t in self.transitions:
            outStates.append(t.outState)
        return outStates


class SimpleTransition:
    def __init__(self, inState, outState, onOutput):
        self.inState = inState
        self.outState = outState
        self.onOutput = onOutput


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

    def getStatus(self):
        return self.status


class TransitionInstance(TransitionStatus):
    def __init__(self, transition, input):
        TransitionStatus.__init__(self)
        self.transition = transition
        self.input = input

    def getCondition(self):
        return self.transition.condition

    def getEvent(self):
        return self.transition.event

    def getInState(self):
        return self.transition.inState

    def getOutState(self):
        return self.transition.outState

    def isMultiChoiceTransition(self):
        return False


class MultiChoiceTransitionInstance(TransitionStatus):
    def __init__(self, multiChoiceTransition, input):
        TransitionStatus.__init__(self)
        self.multiChoiceTransition = multiChoiceTransition
        self.input = input

    def getChoices(self):
        return self.multiChoiceTransition.transitions

    def isMultiChoiceTransition(self):
        return True


class MultiChoiceTransitionBuilder:

    class MultiChoiceConditionBuilder:
        def __init__(self, multiChoiceBuilder, sentence=None):
            self.multiChoiceBuilder = multiChoiceBuilder
            self.transition = Transition()
            self.transition.setCondition(sentence)

        def goTo(self, outStateName):
            outState = self.multiChoiceBuilder.stateChart.states[outStateName]
            self.transition.setOutState(outState)
            isAlreadySync = 1 < len([o for o in self.multiChoiceBuilder.multiChoiceTransition.getOutStates() if outState == o])
            if outState.isSyncState() and not isAlreadySync:
                outState.addSyncCounter()
            return self.multiChoiceBuilder

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


class EventFSMBehaviour(OneShotBehaviour, BeliefListener, EventListener):
    def __init__(self, name):
        super(EventFSMBehaviour, self).__init__(name)
        self.states = dict()
        self.startState = None
        self.transitions = defaultdict(list)
        self.waitingTransitions = list()
        self.stateInstances = dict()
        self.started = False

    def onStart(self):
        print "Liveness statechart started"
        self.myAgent.addBeliefListener(self)
        self.myAgent.addEventListener(self)

    def onEnd(self):
        self.myAgent.removeBeliefListener(self)

    def createState(self, name, action, sync=False):
        state = State(name, action, sync)
        self.states[name] = state

    def createSyncState(self, name, action):
        self.createState(name, action, True)

    def setStartingPoint(self, stateName):
        self.startState = self.states[stateName]

    def createSimpleTransition(self, fromStateName, toStateName, onOutput):
        s1 = self.states[fromStateName]
        s2 = self.states[toStateName]
        self.transitions[s1].append(SimpleTransition(s1, s2, onOutput))
        if s2.isSyncState():
            s2.addSyncCounter()

    def createWaitingTransition(self, fromStateName, toStateName, conditionSentence=None):
        s1 = self.states[fromStateName]
        s2 = self.states[toStateName]
        self.transitions[s1].append(Transition(s1, s2, conditionSentence))
        if s2.isSyncState():
            s2.addSyncCounter()

    def createMultiChoiceWaitingTransition(self):
        return MultiChoiceTransitionBuilder(self)

    def addMultiChoiceTransition(self, multiChoiceTransition):
        self.transitions[multiChoiceTransition.inState].append(multiChoiceTransition)

    def onActionPerformed(self, stateInstance, output):
        self.stateInstances.pop(stateInstance.state, None)
        for transition in self.transitions[stateInstance.getState()]:
            if isinstance(transition, Transition):
                self.performParallelTransition(transition, output)
            elif isinstance(transition, MultiChoiceTransition):
                self.performMultiChoiceTransition(transition, output)
            elif isinstance(transition, SimpleTransition):
                self.performSimpleTransition(transition, output)
            else:
                raise Exception("Unknown transition type")

    def performSimpleTransition(self, transition, output):
        if transition.onOutput == output:

            def transtionCallback(stateInstance, output):
                self.onActionPerformed(stateInstance, output)

            self.executeState(transition.outState, transtionCallback, output, None)


    def performParallelTransition(self, transition, input):
        if transition.event is None and (transition.condition is None or self.myAgent.askBelieve(transition.condition)):

            def transtionCallback(stateInstance, output):
                self.onActionPerformed(stateInstance, output)

            self.executeState(transition.outState, transtionCallback, input, None)
        else:
            self.waitingTransitions.append(TransitionInstance(transition, input))

    def performMultiChoiceTransition(self, multiChoice, input):
        for choice in multiChoice.transitions:
            if choice.event is None and (choice.condition is None or self.myAgent.askBelieve(choice.condition)):

                def transtionCallback(stateInstance, output):
                    self.onActionPerformed(stateInstance, output)

                self.executeState(choice.outState, transtionCallback, input, None)
                break
        else:
            self.waitingTransitions.append(MultiChoiceTransitionInstance(multiChoice, input))

    def executeState(self, state, callback, input, event):
        if state.isSyncState():
            if state not in self.stateInstances:
                self.stateInstances[state] = StateInstance(self, state, callback)
            stateInstance = self.stateInstances[state]
        else:
            stateInstance = StateInstance(self, state, callback)

        stateInstance.addInput(input)
        if event is not None:
            stateInstance.addEventInput(event)

        self.myAgent.getTaskExecutor().addTask(stateInstance)

    def onBeliefChanged(self, sentence):
        for transition in self.waitingTransitions:
            if transition.isWaiting():
                if transition.isMultiChoiceTransition():
                    self.tryToExecuteMultiChoiceTransitionAfterBeliefChange(transition, sentence)
                else:
                    self.tryToExecuteTransitionAfterBeliefChange(transition, sentence)

        self.waitingTransitions = [t for t in self.waitingTransitions if not t.isDone()]

    def onEvent(self, eventType, event):
        for transition in self.waitingTransitions:
            if transition.isWaiting():
                if transition.isMultiChoiceTransition():
                    self.tryToExecuteMultiChoiceTransitionAfterEvent(transition, eventType, event)
                else:
                    self.tryToExecuteTransitionAfterEvent(transition, eventType, event)

        self.waitingTransitions = [t for t in self.waitingTransitions if not t.isDone()]

    def tryToExecuteTransitionAfterBeliefChange(self, transition, change):
        if transition.getCondition() is None or self.myAgent.askBelieve(transition.getCondition()) is True:
            transition.setRunning()

            def transtionCallback(stateInstance, output):
                transition.done()
                self.onActionPerformed(stateInstance, output)

            self.executeState(transition.getOutState(), transtionCallback, transition.input, None)

    def tryToExecuteMultiChoiceTransitionAfterBeliefChange(self, multiChoiceTransition, change):
        for choice in multiChoiceTransition.getChoices():
            if choice.condition is None or self.myAgent.askBelieve(choice.condition):
                multiChoiceTransition.setRunning()

                def transtionCallback(stateInstance, output):
                    multiChoiceTransition.done()
                    self.onActionPerformed(stateInstance, output)

                self.executeState(choice.outState, transtionCallback, multiChoiceTransition.input, None)
                break

    def tryToExecuteTransitionAfterEvent(self, transition, eventType, event):
        if eventType != transition.getEvent():
            return

        if transition.getCondition() is None or self.myAgent.askBelieve(transition.getCondition()) is True:
            transition.setRunning()

            def transtionCallback(stateInstance, output):
                transition.done()
                self.onActionPerformed(stateInstance, output)

            self.executeState(transition.getOutState(), transtionCallback, transition.input, event)

    def tryToExecuteMultiChoiceTransitionAfterEvent(self, multiChoiceTransition, eventType, event):
        for choice in multiChoiceTransition.getChoices():
            if eventType != choice.event:
                continue
            if choice.condition is None or self.myAgent.askBelieve(choice.condition):
                multiChoiceTransition.setRunning()

                def transtionCallback(stateInstance, output):
                    multiChoiceTransition.done()
                    self.onActionPerformed(stateInstance, output)

                self.executeState(choice.outState, transtionCallback, multiChoiceTransition.input, event)
                break

    def process(self):
        if not self.started:
            self.started = True

            def transtionCallback(stateInstance, output):
                self.onActionPerformed(stateInstance, output)

            self.executeState(self.startState, transtionCallback, None, None)

            # sleep(2)
            # print "send EVENT_ORDER_LISTEN"
            # self.myAgent.raiseEvent("EVENT_ORDER_LISTEN", "1")
            # sleep(2)
            # print "send EVENT_TURTLE_SAY"
            # self.myAgent.raiseEvent("EVENT_TURTLE_SAY", self)
            # sleep(2)
            # print "send EVENT_MOVE"
            # self.myAgent.raiseEvent("EVENT_MOVE")
            # sleep(2)
            # print "send EVENT_TURTLE_SAY"
            # self.myAgent.raiseEvent("EVENT_TURTLE_SAY", self)
            # sleep(2)
            # print "send EVENT_MOVE"
            # self.myAgent.raiseEvent("EVENT_MOVE")

    def done(self):
        return self.started
