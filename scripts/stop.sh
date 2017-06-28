#!/usr/bin/env bash
sshpass -p "nao" ssh nao@172.27.96.22 'cd /home/nao/SpadeNao; python StopAgent.py nao1@172.27.96.23'
