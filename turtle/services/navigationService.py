from numpy.distutils.fcompiler.g95 import G95FCompiler

import rospy
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, Point, Quaternion
from geometry_msgs.msg import Twist


class GoToPose:
    def __init__(self):

        self.goal_sent = False

        # What to do if shut down (e.g. Ctrl-C or failure)
        rospy.on_shutdown(self.shutdown)

        # Tell the action client that we want to spin a thread by default
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        rospy.loginfo("Wait for the action server to come up")

        # Allow up to 5 seconds for the action server to come up
        self.move_base.wait_for_server(rospy.Duration(5))

    def goto(self, pos, quat):

        # Send a goal
        self.goal_sent = True
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = 'map'
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose = Pose(Point(pos['x'], pos['y'], 0.000),
                                     Quaternion(quat['r1'], quat['r2'], quat['r3'], quat['r4']))

        # Start moving
        print "sending goal", pos, quat
        self.move_base.send_goal(goal)
        print "goal sent"
        # Allow TurtleBot up to 60 seconds to complete task
        success = self.move_base.wait_for_result(rospy.Duration(60))
        print "moving base finished"
        state = self.move_base.get_state()
        result = False

        if success and state == GoalStatus.SUCCEEDED:
            # We made it!
            result = True
        else:
            self.move_base.cancel_goal()

        self.goal_sent = False
        return result

    def shutdown(self):
        if self.goal_sent:
            self.move_base.cancel_goal()
        rospy.loginfo("Stop")
        rospy.sleep(1)


class HighLevelMoving:
    def __init__(self):
        self.navigator = GoToPose()
        self.cmd_vel = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)

    def allerALaPorte(self):
        position = {'x': -0.309, 'y': -0.769}
        quaternion = {'r1': 0.000, 'r2': 0.000, 'r3': 0.000, 'r4': 1.000}

        rospy.loginfo("Go to (%s, %s) pose", position['x'], position['y'])
        success = self.navigator.goto(position, quaternion)

        if success:
            rospy.loginfo("Hooray, i am next to the door")
        else:
            rospy.loginfo("The base failed to reach the desired pose (door)")

        return success

    def allerAuRadiateur(self):
        position = {'x': -0.1, 'y': 1.5}
        quaternion = {'r1': 0.000, 'r2': 0.000, 'r3': 0.000, 'r4': 1.000}

        rospy.loginfo("Go to (%s, %s) pose", position['x'], position['y'])
        success = self.navigator.goto(position, quaternion)

        if success:
            rospy.loginfo("Hooray, reached the desired pose readiateur")
        else:
            rospy.loginfo("The base failed to reach the desired pose (radiateur)")

        return success

    def pushTheBox(self):
        r = rospy.Rate(10)
        move_cmd = Twist()
        move_cmd.linear.x = -0.1
        move_cmd.angular.z = 0
        for i in range(40):
            self.cmd_vel.publish(move_cmd)
            r.sleep()

    def allerDevantLaBoite(self, other):
        print "here is the other" , other
        position = {}
        if other == "turtleone@127.0.0.1":
            position = {'x': 0.781217940143, 'y': -0.380938133137}
        else:
            position = {'x': 0.780934295942, 'y': 0.280883814842}

        quaternion = {'r1': 0.000, 'r2': 0.000, 'r3': 0.700, 'r4': -0.1}

        rospy.loginfo("Go to (%s, %s) pose", position['x'], position['y'])
        success = self.navigator.goto(position, quaternion)

        if success:
            rospy.loginfo("Hooray, i am next to the door")
        else:
            rospy.loginfo("The base failed to reach the desired pose (door)")

        return success