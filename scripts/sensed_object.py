#!/usr/bin/env python

import numpy as np
import rospy
from sensor_msgs.msg import LaserScan
from math import sqrt, pow
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose2D, Point

destination_x, destination_y = 0, 0
current_x, current_y = 2, 6

def callback(msg, pub):
    global current_x, current_y, destination_x, destination_y
    ranges = msg.ranges

    # convert to numpy array to be able to use numpy functions
    npranges = np.array(ranges)

    # convert values out of range or 'inf' to 'NaN' to be ignored in calculation
    npranges[npranges > msg.range_max] = np.nan
    npranges[npranges < msg.range_min] = np.nan

    # compute minimum distance and its corresponding angles with respect to scanner's frame
    if False in np.isnan(npranges): #at least one element isn't NaN
        d = np.nanmin(npranges)
        indices = np.argwhere(npranges == d).flatten()
        a = ((indices * msg.angle_increment) + msg.angle_min) * 180.0 / np.pi
            
        # Publish sensed object information
        publish_sensed_object(d, a, pub)
    else:
        rospy.loginfo('No objects detected')

def publish_sensed_object(d, a, pub):
    global current_x, current_y, destination_x, destination_y
    msg = Pose2D()
    msg.x = d
    msg.y = distance_calculator(destination_x, destination_y, current_x, current_y)
    msg.theta = a
    rospy.loginfo("x = %f , y = %f, theta = %f", msg.x, msg.y, msg.theta)
    pub.publish(msg)

def distance_calculator(x1, y1, x2, y2):
    print(x1, y1, x2, y2)
    return sqrt(pow((x2 - x1), 2) + pow((y2 - y1), 2))

def set_destination(msg):
    global destination_x, destination_y
    destination_x = msg.x
    destination_y = msg.y

def set_current_pose(msg):
    global current_x, current_y
    current_x = msg.pose.pose.position.x
    current_y = msg.pose.pose.position.y

def main():
    rospy.init_node('sensed_object', anonymous=False)

    rospy.Subscriber('odom', Odometry, set_current_pose)
    rospy.Subscriber('destination', Point, set_destination)

    pub = rospy.Publisher('sensed_object', Pose2D, queue_size=10)
    rospy.Subscriber('scan', LaserScan, callback, pub)

    
    rate = rospy.Rate(10)  # 10 Hz
    while not rospy.is_shutdown():
        rospy.spin()  # Process any incoming messages
        rate.sleep()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
