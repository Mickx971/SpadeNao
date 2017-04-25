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


class MultiChoiceTransition:
    def __init__(self, inState, choices):
        self.inState = inState
        self.choices = choices


class MultiChoiceTransitionInstance:
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
        return self.transition.choices

    def getInState(self):
        return self.transition.inState


class MultiChoiceCondition:
    def __init__(self, sentence):
        self.sentence = sentence
        self.outState = None
        self.isSetted = False

    def setOutState(self, outState):
        self.isSetted = True
        self.outState = outState

    def isSetted(self):
        return self.isSetted


class MultiChoiceTransitionBuilder:

    class MultiChoiceConditionBuilder:
        def __init__(self, multiChoice, sentence=None):
            self.choice = MultiChoiceCondition(sentence)
            self.isSetted = False
            self.multiChoice = multiChoice

        def goTo(self, outStateName):
            self.choice.setOutState(self.multiChoice.stateChart.states[outStateName])
            return self.multiChoice

    def __init__(self, stateChart):
        self.stateChart = stateChart
        self.inState = None
        self.ifDone = False
        self.elseDone = False
        self.inStateSetted = False
        self.choices = list()

    def fromState(self, name):
        if not self.inStateSetted:
            self.inStateSetted = True
            self.inState = self.stateChart.states[name]
            return self
        else:
            raise RuntimeError("fromState already setted")

    def ifCondition(self, sentence):
        if not self.ifDone :
            self.ifDone = True
            builder = self.MultiChoiceConditionBuilder(self, sentence)
            self.choices.append(builder.choice)
            return builder
        else:
            raise RuntimeError("IfCondition already called")

    def elifCondition(self, sentence):
        if self.ifDone and not self.elseDone:
            builder = self.MultiChoiceConditionBuilder(self, sentence)
            self.choices.append(builder.choice)
            return builder
        else:
            raise RuntimeError("IfCondition not yet called")

    def elseCondition(self):
        if self.ifDone and not self.elseDone:
            self.elseDone = True
            builder = self.MultiChoiceConditionBuilder(self)
            self.choices.append(builder.choice)
            return builder
        else:
            raise RuntimeError("IfCondition not yet called")

    def create(self):
        if self.inState is not None and self.ifDone and self.inStateSetted and all(choice.isSetted() for choice in self.choices):
            self.stateChart.addMultiChoiceTransition(MultiChoiceTransition(self.inState, self.choices))
        else:
            raise RuntimeError("Fail to create MultiChoiceTransition")



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
        state = State(self, name, action)
        self.states[name] = state

    def setStartingPoint(self, stateName):
        self.start = self.states[stateName]

    def createTransition(self, fromStateName, toStateName, conditionSentence=None):
        s1 = self.states[fromStateName]
        s2 = self.states[toStateName]
        self.transitions[s1].append(Transition(s1, s2, conditionSentence))

    def createMultiChoiceTransition(self):
        return MultiChoiceTransitionBuilder(self)

    def addMultiChoiceTransition(self, multiChoiceTransition):
        self.transitions[multiChoiceTransition.inState] = list(multiChoiceTransition)

    def onActionPerformed(self, state):
        for transition in self.transitions[state]:
            transitionType = type(transition)
            if transitionType is Transition:
                self.performParallelTransition(transition)
            elif transitionType is MultiChoiceTransition:
                self.performMultiChoiceTransition(transition)
            else:
                raise Exception("Unknown transition type: " + transitionType)

    def performParallelTransition(self, transition):
        if transition.condition is None:
            self.executeState(transition.outState)
        else:
            self.prepareTransition(TransitionInstance(transition))

    def performMultiChoiceTransition(self, transition):
        for choice in transition.choices:
            if self.myAgent.askBelieve(choice.sentence) is True:
                self.executeState(choice.outState)
                break
        else:
            self.prepareTransition(MultiChoiceTransitionInstance(transition))

    def prepareTransition(self, transition):
        if type(transition) is TransitionInstance and self.myAgent.askBelieve(transition.getCondition()) is True:
            self.executeState(transition.getOutState())
        else:
            self.waitingTransitions.append(transition)

    def executeState(self, state):
        self.myAgent.getTaskExecutor().addTask(state)

    def onBeliefChanged(self, sentence):
        for transition in self.waitingTransitions:
            if transition.isWaiting():
                transitionType = type(transition)
                if transitionType is TransitionInstance:
                    self.tryToExecuteTransition(transition)
                elif transitionType is MultiChoiceTransition:
                    self.tryToExecuteMultiChoiceTransition(transition)
                else:
                    raise Exception("Unknown transition type: " + transitionType)

        self.waitingTransitions = [t for t in self.waitingTransitions if not t.isDone()]

    def tryToExecuteTransition(self, transition):
        if self.myAgent.askBelieve(transition.getCondition()) is True:
            transition.setRunning()
            self.executeState(transition.getOutState())

    def tryToExecuteMultiChoiceTransition(self, transition):
        for choice in transition.choices:
            if self.myAgent.askBelieve(choice.sentence) is True:
                transition.setRunning()
                self.executeState(choice.outState)
                break

if __name__ == "__main__":

    def printCoucou():
        print "coucou 1"

    def printBonjour():
        print "bonjour 2"

    def printHello():
        print "hello 3"

    def printHola():
        print "hola 4"

    st = StateChart("Lifeness")
    st.createState("first", printCoucou)
    st.createState("second", printBonjour)
    st.createState("third", printHello)
    st.createState("forth", printHola)
    st.createTransition("first", "second")
    st.createMultiChoiceTransition()\
        .fromState("second")\
            .ifCondition("condition(un)").goTo("third") \
            .elifCondition("condition(deux)").goTo("third")\
            .elseCondition().goTo("forth")\
        .create()
    st.setStartingPoint("first")
