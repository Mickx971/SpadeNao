import rospy
rospy.init_node("raphael")
import spade
from turtle.behaviours.goToBehaviour  import GoToPoseBehaviour
from turtle.behaviours.waitMessageBehaviour import WaitMessageBehaviour
from turtle.agents.turtleAgent.turtleAgent import TurtleAgent
from turtle.behaviours.informNaoBehaviour import InformNaoBehaviour
from turtle.behaviours.communicator import Communicator
from turtle.behaviours.getPositionBehaviour import GetPositionBehaviour
from turtle.behaviours.transformPositionBehaviour import TransformPositionBehaviour
from turtle.behaviours.moveToWithFeedBackBehaviour import MoveToWithFeedBackBehaviour
from turtle.behaviours.testIfNearOtherBehaviour import TestIfNearOtherBehaviour

class TestAgent(TurtleAgent):

    def _setup(self):
        TurtleAgent._setup(self)
        print "agent starting"
        fsmStates = {"waitForMessage": 1, "goToPose": 2, "informNao": 3,
                     "getPosition": 4, "transformPosition": 5,
                     "moveWithFeedBack": 6, "testIfNear": 7}
        fsm = spade.Behaviour.FSMBehaviour()

        fsm.registerFirstState(WaitMessageBehaviour(fsmStates["waitForMessage"]),fsmStates["waitForMessage"])
        fsm.registerState(GoToPoseBehaviour(fsmStates["goToPose"]),fsmStates["goToPose"])
        fsm.registerState(InformNaoBehaviour(fsmStates["informNao"]), fsmStates["informNao"])
        fsm.registerState(GetPositionBehaviour(fsmStates["getPosition"]), fsmStates["getPosition"])


        fsm.registerState(TransformPositionBehaviour(fsmStates["transformPosition"]),
                               fsmStates["transformPosition"])

        fsm.registerState(MoveToWithFeedBackBehaviour(fsmStates["moveWithFeedBack"]),
                          fsmStates["moveWithFeedBack"])

        fsm.registerState(TestIfNearOtherBehaviour(fsmStates["testIfNear"]),
                          fsmStates["testIfNear"])

        fsm.registerTransition(fsmStates["waitForMessage"],fsmStates["goToPose"],WaitMessageBehaviour.goTo)
        fsm.registerTransition(fsmStates["goToPose"], fsmStates["informNao"], 0)
        fsm.registerTransition(fsmStates["informNao"], fsmStates["waitForMessage"], 0)

        fsm.registerTransition(fsmStates["waitForMessage"], fsmStates["getPosition"], WaitMessageBehaviour.goNear)
        fsm.registerTransition(fsmStates["getPosition"], fsmStates["transformPosition"], 0)
        fsm.registerTransition(fsmStates["transformPosition"], fsmStates["moveWithFeedBack"], 0)

        fsm.registerTransition(fsmStates["moveWithFeedBack"], fsmStates["testIfNear"],
                               MoveToWithFeedBackBehaviour.GOAL_REACHED)
        fsm.registerTransition(fsmStates["moveWithFeedBack"], fsmStates["informNao"],
                               MoveToWithFeedBackBehaviour.GOAL_NON_REACHED)

        fsm.registerTransition(fsmStates["testIfNear"], fsmStates["informNao"],
                               TestIfNearOtherBehaviour.Near)
        fsm.registerTransition(fsmStates["testIfNear"], fsmStates["getPosition"],
                               TestIfNearOtherBehaviour.NotNear)
        self.addBehaviour(fsm, None)




if __name__ == "__main__":
    agent = TestAgent("raphael", "127.0.0.1", "secret", receiveBehaviour=Communicator())
    agent.start()