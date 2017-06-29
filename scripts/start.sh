#@IgnoreInspection BashAddShebang
sh scripts/refresh.sh
sh scripts/stop.sh
sshpass -p "nao" ssh nao@172.27.96.22 'cd /home/nao/SpadeNao; source ~/.profile; python MasterAgent.py nao/nao.ini'