from naoqi import ALProxy
import spade


class MasterAgent(spade.Agent.Agent):
    def _setup(self):
        tts = ALProxy("ALTextToSpeech", "192.168.43.102", 9559)
        tts.say("Hello, world!")
        self.logger.info("coucou")


if __name__ == "__main__":
    nao = MasterAgent("nao@192.168.43.171", "secret")
    nao.start()
