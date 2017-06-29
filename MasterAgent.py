# -*- coding: utf-8 -*-
from nao.Nao import NaoAgent
import sys
import json


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print "Error: No config file"
        print "Usage: python MasterAgent.py path/to/config/file.ini"
        exit(1)

    config = json.loads(open(sys.argv[1]).read())

    naoAgent = NaoAgent(config["agentName"], config["plateformIp"], config["plateformSecret"], config["naoIp"])
    naoAgent.start()

