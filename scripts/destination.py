#!/usr/bin/env python

## Prompts the user of the (x, y) coordinates of the robot's destination point
## in the 2D space and publishes it to the topic "/destination"
import rospy
from geometry_msgs.msg import Point

def publish_dest_coordinates(x, y):
    rospy.init_node("destination", anonymous=False)
    pub = rospy.Publisher('destination', Point, queue_size=10)
    rate = rospy.Rate(1)
    msg = Point()
    msg.x = x
    msg.y = y

    while not rospy.is_shutdown():
        rospy.loginfo("Destination coordinates are (" + str(msg.x) + ", " + str(msg.y) + " )")
        pub.publish(msg)
        rate.sleep()

def get_dest_coordinates():
    x, y = -11, -11  
    while (x < -10 or x > 10):
        x = float(input("Please enter the value of x coordinate of the robot's destination in the range (-10m, 10m): "))
    while (y < -10 or y > 10):
        y = float(input("Please enter the value of y coordinate of the robot's destination in the range (-10m, 10m): "))
    publish_dest_coordinates(x, y)

if __name__ == '__main__':
    try:
        get_dest_coordinates()
    except rospy.ROSInterruptException:
        pass
