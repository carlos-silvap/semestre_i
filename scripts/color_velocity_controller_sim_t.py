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
        klinear = 50
        self.rad = msg.data
           
        if (self.rad > 30) :
            self.robot_vel.linear.x=0 
            self.count=0
            
        elif (self.rad==self.prev):
            self.count=self.count+1 
            if(self.count>6):
                self.robot_vel.linear.x=0
                self.robot_vel.angular.z=0 
        
        else:
            self.robot_vel.linear.x = klinear / (self.rad+0.00001)
            if (self.rad != self.prev):
                self.count=0    
                        
        self.prev=self.rad
               
        print (self.count)
      
        
        
    def center_cb(self, msg):  
        kangular = 0.01
        self.x0 = 300
        self.center_x = msg.x
        self.xdiff =self.x0-self.center_x
        if(self.count<6 or self.rad < 30):
            self.robot_vel.angular.z = kangular * self.xdiff
        
        
       
    def cleanup(self): 
        print('apagando motor')
        self.robot_vel.angular.z = 0
        self.robot_vel.linear.x = 0
      
       
        
############################### MAIN PROGRAM ####################################  
if __name__ == "__main__":  

    rospy.init_node("color_velocity_controller", anonymous=True)  
    ColorVelControl() 

