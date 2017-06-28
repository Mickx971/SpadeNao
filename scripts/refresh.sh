#@IgnoreInspection BashAddShebang
sshpass -p "nao" scp -r -p $(find *) nao@172.27.96.22:/home/nao/SpadeNao
sshpass -p "nao" ssh nao@172.27.96.22 'cd /home/nao/SpadeNao; python -m compileall .'