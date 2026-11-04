#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist, Point, Pose2D
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion
from math import atan2, sqrt, pi

class Bug0Drive:
    def __init__(self):
        self.e = 0.3  # Distance threshold to start circumventing an obstacle
        self.epsilon = 0.1  # Distance threshold to goal to consider it reached

        self.goal_reached = False
        self.destination = Point()
        self.current_pose = Point()
        self.current_yaw = 0.0
        self.closest_object_distance = float('inf')
        self.circumvent_direction = 'right'  # 'right' or 'left' to circumvent
        self.closest_object_angle = None
        self.distance_to_destination = 10000

        # Initialize ROS node
        rospy.init_node('drive_robot', anonymous=False)
        # Subscribe to necessary topics
        rospy.Subscriber('destination', Point, self.set_destination)
        rospy.Subscriber('sensed_object', Pose2D, self.set_nearest_object)  # Assuming sensed_object topic provides distance (x) and direction (y)
        rospy.Subscriber('odom', Odometry, self.set_robot_pose)
        # Publisher to send velocity commands
        self.pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
        # Start the main loop
        self.bug0_algorithm()
        
    def set_destination(self, msg):
        self.destination = msg

    def set_robot_pose(self, msg):
        self.current_pose = msg.pose.pose.position
        orientation_q = msg.pose.pose.orientation
        orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
        _, _, self.current_yaw = euler_from_quaternion(orientation_list)

    def set_nearest_object(self, msg):
        # Assuming msg.x contains the distance to the nearest object and is not 'NaN'
        self.closest_object_distance = msg.x
        # Assuming msg.y contains the bearing to the nearest object relative to the robot's current orientation
        self.closest_object_angle = msg.theta
        # Compute the distance to the destination
        self.distance_to_destination = msg.y

    def bug0_algorithm(self):
        rate = rospy.Rate(20)  # 20 Hz

        # Wait for the subscribers to receive messages and set attributes
        while (self.destination is None or
            self.current_pose is None or
            self.distance_to_destination == 0 or
            self.closest_object_distance == float('inf')):
            rospy.loginfo("Waiting for initial data...")
            rate.sleep()

        # Now all required attributes are set, proceed with the algorithm
        while not self.goal_reached and not rospy.is_shutdown():
            if self.distance_to_destination <= self.epsilon:
                rospy.loginfo("Goal Reached")
                self.goal_reached = True
                msg = Twist()
                
                msg.linear.x = 0  
                msg.angular.z = 0
                self.pub.publish(msg)
                break

            # Check if there's an obstacle close by
            if self.closest_object_distance > self.e:
                # No obstacle detected within threshold, move towards destination
                self.move_to_destination()
            else:
                # Obstacle detected, circumvent it
                self.circumvent_obstacle()

            rate.sleep()

    def move_to_destination(self):
        msg = Twist()
        msg.linear.x = 0.2
        print("current pose ", self.current_pose)
        angle_to_destination = atan2(
            self.destination.y - self.current_pose.y,
            self.destination.x - self.current_pose.x
        )
        msg.angular.z = self.angle_difference(angle_to_destination, self.current_yaw)
        self.pub.publish(msg)

    def circumvent_obstacle(self):
        print("turning!!!!!!!!!!turning!!!!!!!!!!")
        msg = Twist()
        print("self.closest_object_angle", self.closest_object_angle, "elf.closest_object_distance ", self.closest_object_distance  )
        if (self.closest_object_angle <= 170 and self.closest_object_angle >= 80) and self.closest_object_distance <= self.e:
            print("move forward!!!!!!!!!!")

            msg.linear.x = 0.1
            msg.angular.z = 0
        else:
            print("stoooooooppppp!!!!!!!!!!turning!!!!!!!!!!")

            msg.linear.x = 0  # Stop linear movement while turning
            turn_speed = -0.5 if self.circumvent_direction == 'right' else 0.5
            msg.angular.z = turn_speed
        self.pub.publish(msg)

    def angle_difference(self, target_angle, current_angle):
        diff = target_angle - current_angle
        while diff > 3.14:
            diff -= 6.28
        while diff < -3.14:
            diff += 6.28
        return diff

if __name__ == '__main__':
    try:
        bug0_drive = Bug0Drive()
    except rospy.ROSInterruptException:
        pass



















# #!/usr/bin/env python

# import rospy
# from geometry_msgs.msg import Twist, Pose2D, Point
# from nav_msgs.msg import Odometry
# from tf.transformations import euler_from_quaternion
# from math import atan2

# class Bug0Drive:
#     def __init__(self):
#         self.e = 0.3 #float(input("Please enter the value of e: "))
#         self.epsilon = 0.1 #float(input("Please enter the value of epsilon: "))

#         self.goal_reached = False
#         self.destination = None
#         self.current_pose = None
#         self.closest_object_distance = float('inf')
#         self.closest_object_angle = None
#         self.circumvent_direction = 'right' #select only one direction ('right' or 'left')
#         self.distance_to_destination = 0
#         rospy.init_node('drive_robot', anonymous = False)
#         rospy.Subscriber('destination', Point, self.set_destination)
#         rospy.Subscriber('sensed_object', Pose2D, self.set_nearest_object)
#         rospy.Subscriber('odom', Odometry, self.set_robot_pose)
#         self.pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
#         self.bug0_algorithm()
        
        
#     def set_destination(self, msg):
#         print("msgggg for destination", msg)
#         self.destination = msg

#     def set_robot_pose(self, msg):
#         self.current_pose = msg.pose.pose.position
#         orientation_q = msg.pose.pose.orientation
#         orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
#         _, _, self.current_yaw = euler_from_quaternion(orientation_list)

#     def set_nearest_object(self, msg):
#         if msg.x != 'NaN':
#             if msg.x < self.closest_object_distance:
#                 self.closest_object_distance = msg.x
#                 self.closest_object_angle = msg.theta
#         else:
#             self.closest_object_distance = float('inf')
#             self.closest_object_angle = None
#         print("hahahahahaaaa", msg.y)
#         self.distance_to_destination = msg.y
        

#     def bug0_algorithm(self):
#         rate = rospy.Rate(20)  # 20 Hz
        
#         while (self.destination is None or
#            self.current_pose is None or
#            self.distance_to_destination == 0 or
#            self.closest_object_distance == float('inf')):
#             rospy.loginfo("Waiting for initial data...")
#             rate.sleep()
#         print("destination ", self.destination)
#         print("dist ", self.distance_to_destination)

#         while not self.goal_reached and not rospy.is_shutdown():
#             if self.destination is None == 0:
#                 rospy.loginfo("Waiting for destination...")
#                 rate.sleep()
#                 continue

#             if self.distance_to_destination <= self.epsilon:
#                 print("Goal Reached")
#                 self.goal_reached = True
#                 break

#             if self.closest_object_distance > self.e:
#                 self.move_to_destination()
#             else:
#                 self.circumvent_obstacle()

#             rate.sleep()

#     def move_to_destination(self):
#         msg = Twist()
#         msg.linear.x = 0.2  
#         print("destination points ", self.destination)
#         print("current pose ", self.current_pose)
#         angle_to_destination = atan2(self.destination.y - self.current_pose.y,
#                                       self.destination.x - self.current_pose.x)
#         msg.angular.z = self.angle_difference(angle_to_destination, self.current_yaw)
#         self.pub.publish(msg)

#     def circumvent_obstacle(self):
#         print("gonna move away!!!!!!!!!!!!!!")
#         if self.closest_object_angle is None:
#             rospy.loginfo("No obstacle detected!")
#             return

#         # if self.circumvent_direction is None:
#         #     # Choose circumvention direction based on current orientation
#         #     if self.current_yaw > 0:
#         #         self.circumvent_direction = 'left'
#         #     else:
#         #         self.circumvent_direction = 'right'

#         msg = Twist()
#         msg.linear.x = 0  # Example linear velocity, adjust as needed
#         if self.circumvent_direction == 'left':
#             msg.angular.z = 0.1
#             # msg.linear.x = 0.01  # Example linear velocity, adjust as needed

#         else:
#             msg.angular.z = -0.1
#             # msg.linear.x = 0.01  # Example linear velocity, adjust as needed

#         self.pub.publish(msg)

#     def angle_difference(self, target_angle, current_angle):
#         diff = target_angle - current_angle
#         if diff > 3.14:
#             diff -= 6.28
#         elif diff < -3.14:
#             diff += 6.28
#         return diff

#     # def run(self):
#     #     self.bug0_algorithm()

# if __name__ == '__main__':
#     try:
#         bug0_drive = Bug0Drive()
#     except rospy.ROSInterruptException:
#         pass
