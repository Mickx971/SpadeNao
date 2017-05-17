from community.core import OneShotBehaviour
import json
import spade

class GetPositionBehaviour(OneShotBehaviour):

    def process(self):
        print "process"
        other = self.myAgent.getData("knowledge")["other"]
        receiver = spade.AID.aid(other,
                                 ["xmpp://"+other])
        self.myAgent.setData("otherPosition",self.getAgentPosition(receiver))

    def getAgentPosition(self, agentAid):
        positionRequest = spade.ACLMessage.ACLMessage()
        positionRequest.setPerformative("request")
        positionRequest.setOntology("position")
        positionRequest.setContent("position")
        positionRequest.addReceiver(agentAid)
        response = self.myAgent.sendMessageAndWaitForResponse(positionRequest)
        response = json.loads(response.getContent())
        return response