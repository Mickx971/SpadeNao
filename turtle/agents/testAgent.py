import rospy
rospy.init_node("turtle1")
import spade
import json
import re
from turtle.behaviours.goToBehaviour  import GoToPoseBehaviour
from turtle.agents.waitMessageBehaviour import WaitMessageBehaviour
from community.core import OneShotBehaviour
from turtle.agents.turtleAgent.turtleAgent import TurtleAgent



class TestAgent(TurtleAgent):

    def _setup(self):
        TurtleAgent._setup(self)
        print "agent starting"
        fsmStates = {"initial": 0,"waitForMessage": 1, "goToPose": 2}
        fsm = spade.Behaviour.FSMBehaviour()

        fsm.registerFirstState(WaitMessageBehaviour(fsmStates["waitForMessage"]),fsmStates["waitForMessage"])
        fsm.registerState(GoToPoseBehaviour(fsmStates["goToPose"]),fsmStates["goToPose"])

        fsm.registerTransition(fsmStates["waitForMessage"],fsmStates["goToPose"],0)
        fsm.registerTransition(fsmStates["goToPose"], fsmStates["waitForMessage"], 0)
        self.addBehaviour(fsm, None)





if __name__ == "__main__":
    agent = TestAgent("turtle1", "127.0.0.1", "secret")
    agent.start()