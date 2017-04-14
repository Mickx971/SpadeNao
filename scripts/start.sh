#@IgnoreInspection BashAddShebang
sh scripts/refresh.sh
sh scripts/stop.sh
sshpass -p "nao" ssh nao@192.168.43.102 'cd /home/nao/SpadeNao; python MasterAgent.py'