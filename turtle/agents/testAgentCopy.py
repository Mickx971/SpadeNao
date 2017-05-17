import rospy
rospy.init_node("turtle1")
import spade
import json
import re
from turtle.behaviours.goToBehaviour  import GoToPoseBehaviour
from turtle.agents.waitMessageBehaviour import WaitMessageBehaviour
from community.core import OneShotBehaviour




class TestAgent(spade.Agent.Agent):

    def __init__(self, agent, password):
        spade.Agent.Agent.__init__(self, agent, password)
        self.data = {}
        self.name = re.search('(.*)@.+', agent).group(1)
        with open("knowledge.json") as knowledge:
             self.data["knowledge"] = json.load(knowledge)[self.name]
        self.data["goals"] = {}


    def _setup(self):
        print "agent starting"
        fsmStates = {"initial": 0,"waitForMessage": 1, "goToPose": 2}
        fsm = spade.Behaviour.FSMBehaviour()

        fsm.registerFirstState(OneShotBehaviour(fsmStates["initial"]),fsmStates["initial"])
        fsm.registerState(WaitMessageBehaviour(fsmStates["waitForMessage"]),fsmStates["waitForMessage"])
        fsm.registerState(GoToPoseBehaviour(fsmStates["goToPose"]),fsmStates["goToPose"])

        fsm.registerTransition(fsmStates["initial"], fsmStates["waitForMessage"], 0)
        fsm.registerTransition(fsmStates["waitForMessage"],fsmStates["goToPose"],0)
        fsm.registerTransition(fsmStates["goToPose"], fsmStates["waitForMessage"], 0)

        template = spade.Behaviour.ACLTemplate()
        mt = spade.Behaviour.MessageTemplate(template)
        self.addBehaviour(fsm, mt)





if __name__ == "__main__":
    agent = TestAgent("turtle1@127.0.0.1", "secret")
    agent.start()