from community.core import OneShotBehaviour
import json
import spade

class GetPositionBehaviour(OneShotBehaviour):

    def process(self):
        print "process"
        other = self.myAgent.getData("otherTurtleAid")
        self.myAgent.setData("otherPosition", self.getAgentPosition(other))

    def getAgentPosition(self, agentAid):
        positionRequest = spade.ACLMessage.ACLMessage()
        positionRequest.setPerformative("request")
        positionRequest.setOntology("position")
        positionRequest.setContent("position")
        positionRequest.addReceiver(agentAid)
        response = self.myAgent.communicator.sendMessageAndWaitForResponse(positionRequest)
        response = json.loads(response.getContent())
        return response
