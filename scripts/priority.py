#!/usr/bin/env python  

import rospy  
import std_msgs
import time 
from std_msgs.msg import Int32
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Point

#This class follows a color object

class Priority():  

    def __init__(self):  

        rospy.on_shutdown(self.cleanup)  

        print "Node started..."  
        
        
        ###******* INIT PUBLISHERS *******###  

        print "Setting publisher..."  

        ##  pub = rospy.Publisher('setPoint', UInt16MultiArray, queue_size=1)  

        self.cmd_vel_pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)  

        print "Publishers ok"  

        print "Starting Node..."  

        ############################### SUBSCRIBERS #####################################  

        rospy.Subscriber("lidar_avoid", Twist, self.avoid_cb)  
        rospy.Subscriber("tracker_follow", Twist, self.follow_cb)   
         

        ############ CONSTANTS ################ 
        self.robot_vel = Twist()
        self.robot_vel.linear.x = 0
        self.robot_vel.angular.z = 0.0
        self.cb1 = 0
        self.cb2 = 0
        self.time=0
        #********** INIT NODE **********###  
        r = rospy.Rate(10) #1Hz  
        
        while not rospy.is_shutdown():  
            self.time= time.time()
            self.cmd_vel_pub.publish(self.robot_vel)
            print(self.robot_vel)
            if self.time-self.cb1 > 2.5:
                self.undetected()
            r.sleep()  
            
            pass
    def undetected(self):
        if self.time - self.cb2 > 1:
            print("lost")
            self.robot_vel.linear.x = 0
            self.robot_vel.angular.z = 0.15
    
    def avoid_cb(self, msg):  
        print("avoiding")
        self.cb1 = time.time()
        self.robot_vel= msg

            
    def follow_cb(self, msg):  
        self.cb2 = time.time()
        if self.cb2 -self.cb1 > 1:
            self.robot_vel= msg
            print("following")
        
    

    def cleanup(self):  
        
        self.robot_vel.linear.x = 0
        self.robot_vel.angular.z = 0.0
        
        pass  

############################### MAIN PROGRAM ####################################  

if __name__ == "__main__":  

    rospy.init_node("priority_control", anonymous=False)  
    Priority()  

 
