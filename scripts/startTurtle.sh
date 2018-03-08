password=turtlebot
if [ $# -eq 0 ]
then
	echo "expected at least one parameter, given 0"
	exit 1
elif [ $# -gt 3 ]
then
	echo "expected at most 3 parameters, given" $#
	exit 1
elif [ $# -eq 3 ]
then
	password=$3
fi
gnome-terminal -e "sshpass -p $password ssh $1@$2 'ls; sleep 10; roslaunch turtlebot_bringup minimal.launch'" &
sleep 10
gnome-terminal -e "sshpass -p $password ssh $1@$2 'roslaunch turtlebot_navigation amcl_demo.launch map_file:=/home/$1/maps/espace_technologique.yaml'" &
