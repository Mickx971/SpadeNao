#!/usr/bin/env bash
sshpass -p "nao" ssh nao@192.168.43.102 'cd /home/nao/SpadeNao; python StopAgent.py nao1@192.168.43.171'
