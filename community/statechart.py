from collections import defaultdict
from community.core import OneShotBehaviour
from community.structure import Task
from community.structure import *
from time import sleep


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

    def run(self):
        if self.syncCounter == self.state.syncCounter:
            self.state.action(self.stateChart.myAgent)
            self.callback(self)
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
    def __init__(self, transition):
        TransitionStatus.__init__(self)
        self.transition = transition

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

    def onActionPerformed(self, stateInstance):
        self.stateInstances.pop(stateInstance.state, None)
        for transition in self.transitions[stateInstance.getState()]:
            if isinstance(transition, Transition):
                self.performParallelTransition(transition)
            elif isinstance(transition, MultiChoiceTransition):
                self.performMultiChoiceTransition(transition)
            else:
                raise Exception("Unknown transition type")

    def performParallelTransition(self, transition):
        if transition.event is None and (transition.condition is None or self.myAgent.askBelieve(transition.condition)):

            def transtionCallback(stateInstance):
                self.onActionPerformed(stateInstance)

            self.executeState(transition.outState, transtionCallback)
        else:
            self.waitingTransitions.append(TransitionInstance(transition))

    def performMultiChoiceTransition(self, multiChoice):
        for choice in multiChoice.transitions:
            if choice.event is None and (choice.condition is None or self.myAgent.askBelieve(choice.condition)):

                def transtionCallback(stateInstance):
                    self.onActionPerformed(stateInstance)

                self.executeState(choice.outState, transtionCallback)
                break
        else:
            self.waitingTransitions.append(MultiChoiceTransitionInstance(multiChoice))

    def executeState(self, state, callback):
        if state.isSyncState():
            if state not in self.stateInstances:
                self.stateInstances[state] = StateInstance(self, state, callback)
            stateInstance = self.stateInstances[state]
        else:
            stateInstance = StateInstance(self, state, callback)
        self.myAgent.getTaskExecutor().addTask(stateInstance)

    def onBeliefChanged(self, sentence):
        self.onChange(sentence)

    def onEvent(self, event):
        self.onChange(event, True)

    def onChange(self, change, isEvent=False):
        for transition in self.waitingTransitions:
            if transition.isWaiting():
                if transition.isMultiChoiceTransition():
                    self.tryToExecuteMultiChoiceTransition(transition, change, isEvent)
                else:
                    self.tryToExecuteTransition(transition, change, isEvent)

        self.waitingTransitions = [t for t in self.waitingTransitions if not t.isDone()]

    def tryToExecuteTransition(self, transition, change, isEvent):
        if isEvent and not change == transition.getEvent():
            return

        if transition.getCondition() is None or self.myAgent.askBelieve(transition.getCondition()) is True:
            transition.setRunning()

            def transtionCallback(stateInstance):
                transition.done()
                self.onActionPerformed(stateInstance)

            self.executeState(transition.getOutState(), transtionCallback)

    def tryToExecuteMultiChoiceTransition(self, multiChoiceTransition, change, isEvent):
        for choice in multiChoiceTransition.getChoices():
            if isEvent and not change == choice.event:
                continue
            if choice.condition is None or self.myAgent.askBelieve(choice.condition):
                multiChoiceTransition.setRunning()

                def transtionCallback(stateInstance):
                    multiChoiceTransition.done()
                    self.onActionPerformed(stateInstance)

                self.executeState(choice.outState, transtionCallback)
                break

    def process(self):
        if not self.started:
            self.started = True

            def transtionCallback(stateInstance):
                self.onActionPerformed(stateInstance)

            self.executeState(self.startState, transtionCallback)

            sleep(2)
            print "send EVENT_ORDER_LISTEN"
            self.myAgent.raiseEvent("EVENT_ORDER_LISTEN")
            self.myAgent.addBelieve("coucou")
            sleep(4)
            self.myAgent.raiseEvent("EVENT_ORDER_LISTEN")
            sleep(2)
            print "send EVENT_ORDER_SIT_DOWN"
            self.myAgent.raiseEvent("EVENT_ORDER_SIT_DOWN")
            self.myAgent.addBelieve("bonjour")
            self.myAgent.removeBelieve("coucou")
            sleep(4)
            self.myAgent.raiseEvent("EVENT_ORDER_SIT_DOWN")
            print "send EVENT_ORDER_SAY_HI"
            self.myAgent.raiseEvent("EVENT_ORDER_SAY_HI")
            sleep(2)
            print "send EVENT_ORDER_LISTEN"
            self.myAgent.raiseEvent("EVENT_ORDER_LISTEN")
            sleep(2)
            print "send EVENT_ORDER_STAND_UP"
            self.myAgent.raiseEvent("EVENT_ORDER_STAND_UP")
            sleep(2)
            print "send EVENT_ORDER_LISTEN"
            self.myAgent.raiseEvent("EVENT_ORDER_LISTEN")
            sleep(2)
            print "send EVENT_ORDER_SIT_DOWN"
            self.myAgent.raiseEvent("EVENT_ORDER_SIT_DOWN")
            sleep(2)
            print "send EVENT_ORDER_LISTEN"
            self.myAgent.raiseEvent("EVENT_ORDER_LISTEN")
            sleep(2)
            print "send EVENT_ORDER_SIT_DOWN"
            self.myAgent.raiseEvent("EVENT_ORDER_SIT_DOWN")
            sleep(2)
            print "send EVENT_ORDER_LISTEN"
            self.myAgent.raiseEvent("EVENT_ORDER_LISTEN")
            sleep(2)
            print "send EVENT_ORDER_SIT_DOWN"
            self.myAgent.raiseEvent("EVENT_ORDER_SIT_DOWN")
            sleep(2)
            print "send EVENT_ORDER_LISTEN"
            self.myAgent.raiseEvent("EVENT_ORDER_LISTEN")
            sleep(2)
            print "send EVENT_ORDER_SIT_DOWN"
            self.myAgent.raiseEvent("EVENT_ORDER_SIT_DOWN")
            sleep(2)
            print "send EVENT_ORDER_LISTEN"
            self.myAgent.raiseEvent("EVENT_ORDER_LISTEN")
            sleep(2)
            print "send EVENT_ORDER_SAY_HI"
            self.myAgent.raiseEvent("EVENT_ORDER_SAY_HI")
            sleep(2)
            print "send EVENT_ORDER_LISTEN"
            self.myAgent.raiseEvent("EVENT_ORDER_LISTEN")
            sleep(2)
            print "send EVENT_ORDER_STAND_UP"
            self.myAgent.raiseEvent("EVENT_ORDER_STAND_UP")

    def done(self):
        return self.started
