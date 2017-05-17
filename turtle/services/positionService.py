import rospy
import tf


class PositionService:

    @staticmethod
    def getCurrentPosition():
        listener = tf.TransformListener()
        rate = rospy.Rate(1)
        for i in range(1, 10):
            try:
                (trans, rot) = listener.lookupTransform("/map", "/base_link", rospy.Time(0))
                return trans, rot
            except KeyboardInterrupt:
                return [], []
            except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
                print "exception1"
                print i
                rate.sleep()
        return [], []

    @staticmethod
    def getBehidPosition(position):
        p = position
        p["position"][0] = p["position"][0] - 0.1
        return p



if __name__ == "__main__":
    rospy.init_node("test_positionService")
    (trans, rot) = PositionService.getCurrentPosition()
    print str(trans)
