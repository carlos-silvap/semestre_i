#!/usr/bin/env python

import rospy
from std_msgs.msg import Int32
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Point

#This class follows an object
class ColorVelControl():  
    def __init__(self): 
        rospy.on_shutdown(self.cleanup)  
            
        ############################### SUBSCRIBERS #####################################  
        rospy.Subscriber("radius", Int32, self.radius_cb) 
        rospy.Subscriber("center", Point, self.center_cb) 
        
        ####  PUBLISHERS ###
        self.cmd_vel_pub=rospy.Publisher("cmd_vel", Twist, queue_size = 1)
        
        ### CONSTANTS ###
        self.robot_vel = Twist()
        self.robot_vel.angular.z = 0
        self.robot_vel.linear.x = 0
        r = rospy.Rate(10) #10 Hz       
        self.prev=0
        self.count=0
        
        ### INIT NODE ####  
        while not rospy.is_shutdown():
            print (self.robot_vel)
            self.cmd_vel_pub.publish(self.robot_vel)
            r.sleep()
            
    def radius_cb(self, msg):  
        klinear = 300
        self.rad = msg.data
        x=0
        
        if (self.rad > 150) :
            self.robot_vel.angular.z=0 
            
        elif (self.rad==self.prev and self.count>10):
            self.robot_vel.linear.x=0
            self.robot_vel.angular.z=0 
        
        else:
            self.robot_vel.angular.z = klinear / (self.rad+0.00001)
            self.cont=0
        self.prev=self.rad
        self.count=self.count+1
        print (self.count)
        pass
        
        
    def center_cb(self, msg):  
        kangular = 0.009
        self.x0 = 300
        self.center_x = msg.x
        self.xdiff =self.x0-self.center_x
        self.robot_vel.linear.x = kangular * self.xdiff
        print("Msg.x", msg.x)
        print("Diff", self.xdiff)
        
       
    def cleanup(self): 
       self.robot_vel.angular.z = 0
       self.robot_vel.linear.x = 0
       pass
       
        
############################### MAIN PROGRAM ####################################  
if __name__ == "__main__":  

    rospy.init_node("color_velocity_controller", anonymous=True)  
    ColorVelControl() 

