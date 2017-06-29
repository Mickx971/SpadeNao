package camera;

import jade.core.Agent;

public class CameraAgent extends Agent {

	private static final long serialVersionUID = 1023877410565436379L;
	private MainCameraBehaviour mainBehaviour;

	@Override
	protected void setup() {
		this.mainBehaviour = new MainCameraBehaviour();
		this.addBehaviour(mainBehaviour);
	}
}
