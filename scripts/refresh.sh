#@IgnoreInspection BashAddShebang
sshpass -p "nao" scp -r -p $(find *) nao@192.168.43.102:/home/nao/SpadeNao
sshpass -p "nao" ssh nao@192.168.43.102 'cd /home/nao/SpadeNao; python -m compileall .'
