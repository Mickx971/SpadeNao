package camera;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import jade.core.AID;
import jade.core.behaviours.Behaviour;
import jade.core.behaviours.ParallelBehaviour;
import jade.core.behaviours.ThreadedBehaviourFactory;
import jade.lang.acl.ACLMessage;

public class MainCameraBehaviour extends ParallelBehaviour {

	private static final long serialVersionUID = -1439016962591502310L;

	public MainCameraBehaviour() {
		super(ParallelBehaviour.WHEN_ALL);
		
		Consumer<JSONObject> classifyEventCallback = this::analyseClassifyEvent;
		Consumer<JSONObject> facesEventCallback = this::analyseFacesEvent;
		
		Behaviour classifyBehaviour = new ThreadedBehaviourFactory().wrap(new DirEventWatcher("/Users/mickx/Desktop/motion/motionClassify", classifyEventCallback));
		Behaviour facesBehaviour = new ThreadedBehaviourFactory().wrap(new DirEventWatcher("/Users/mickx/Desktop/motion/motionFaces", facesEventCallback));
				
		this.addSubBehaviour(classifyBehaviour);
		this.addSubBehaviour(facesBehaviour);
	}

	public void analyseClassifyEvent(JSONObject obj) {
		try {
			JSONArray arr = obj.getJSONArray("classifiers").getJSONObject(0).getJSONArray("classes");
			double prob = 1;
			List<String> classes = new ArrayList<>();
			for(int i = 0; i < arr.length(); i++) {
				JSONObject o = arr.getJSONObject(i);
				prob *= o.getDouble("score");
				classes.add(o.getString("class"));
			}
			sendClassifyEvent(prob, classes);
		} catch (JSONException e) {
			e.printStackTrace();
		}
	}
	
	public void analyseFacesEvent(JSONObject obj) {
		try {
			
			int nbFemale = 0;
			int nbFaces = 0;
			int nbMale = 0;
			double prob = 1;
			
			JSONArray arr = obj.getJSONArray("faces");
			for(int i = 0; i < arr.length(); i++) {
				JSONObject o = arr.getJSONObject(i);
				JSONObject gender = o.getJSONObject("gender");
				
				if(gender.getString("gender").equals("FEMALE")) {
					nbFemale++;
				}
				else {
					nbMale++;
				}
				
				prob *= gender.getDouble("score");
			}
			
			nbFaces = arr.length();
			
			sendFacesEvent(nbFaces, nbFemale, nbMale, prob);
			
		} catch (JSONException e) {
			e.printStackTrace();
		}
	}

	private void sendFacesEvent(int nbFaces, int nbFemale, int nbMale, double prob) throws JSONException {
		JSONObject data = new JSONObject()
				.put("action", "detect_faces")
				.put("nbFaces", nbFaces)
				.put("nbFemale", nbFemale)
				.put("nbMale", nbMale)
				.put("prob", prob)
				.put("test1", true);
		sendMessage(data.toString());
	}
	
	private void sendClassifyEvent(double prob, List<String> classes) throws JSONException {
		JSONObject data = new JSONObject()
				.put("action", "classify")
				.put("prob", prob)
				.put("classes", classes);
		sendMessage(data.toString());
	}
	
	private void sendMessage(String content) {
		System.out.println(content);
		ACLMessage msg = new ACLMessage(ACLMessage.INFORM);
		AID agentAdress = new AID("nao1@192.168.43.170", AID.ISGUID);
		agentAdress.addAddresses("http://nao1@192.168.43.170:2099");
		msg.addReceiver(agentAdress);
		msg.setOntology("cameraOntology");
		msg.setContent(content);
		myAgent.send(msg);
	}
}
