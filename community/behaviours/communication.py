import spade
from community.core import Behaviour


class Communicator(Behaviour):
    def __init__(self):
        super(Communicator, self).__init__("Communicator")

    def _process(self):
        pass