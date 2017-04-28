# -*- coding: utf-8 -*-
from nao.Nao import NaoAgent


if __name__ == "__main__":

    NAO_NAME = "nao1"
    PLATFORM_IP = "192.168.43.170"
    SECRET = "secret"
    SELF_IP = "192.168.43.102"
    naoAgent = NaoAgent(NAO_NAME, PLATFORM_IP, SECRET, SELF_IP)
    naoAgent.start()

