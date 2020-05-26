#!/usr/bin/env python

import rospy
from std_msgs.msg import Int32
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Point
from sensor_msgs.msg import LaserScan


#This class controls velocity
class TotalControlClass():  
    def __init__(self): 
        rospy.on_shutdown(self.cleanup)  
            
        ############################### SUBSCRIBERS #####################################  
        rospy.Subscriber("base_scan", LaserScan, self.base_scan_cb)
        rospy.Subscriber("radius", Int32, self.radius_cb) 
        rospy.Subscriber("center", Point, self.center_cb) 
        
        ####  PUBLISHERS ###
        self.cmd_vel_pub=rospy.Publisher("cmd_vel", Twist, queue_size = 1)
        
        ### CONSTANTS ###
        self.robot_vel = Twist()
        self.robot_vel.angular.z = 0
        self.robot_vel.linear.x = 0
        self.flag = False
        self.color_dist = 0
        
        r = rospy.Rate(10) #10 Hz       
        
        
        ### INIT NODE ####  
        while not rospy.is_shutdown():
            print (self.robot_vel)
            self.cmd_vel_pub.publish(self.robot_vel)
            r.sleep()
            
    def radius_cb(self, msg):  
        self.rad = msg.data
        
    def center_cb(self, msg): 
        #constant of the angular velocity
        kangular = 0.005
        #center limits
        lim_sup_cent = 315
        lim_inf_cent = 285
        #x image center
        self.x0 = 300
        #object center
        self.center_x = msg.x
        self.xdiff =self.x0-self.center_x
       
        if(self.center_x < lim_sup_cent and self.center_x > lim_inf_cent):
            self.flag = True
            self.robot_vel.angular.z = 0
        
        else:
            self.flag = False
            self.robot_vel.angular.z = kangular * self.xdiff
            
            
            if (self.color_dist  < 0.30):
                self.robot_vel.linear.x = 0
                self.robot_vel.linear.x = self.robot_vel.linear.x - 0.1
       
    def base_scan_cb(self, msg): 
        #constant of the linear velocity
        klinear = 0.2
        #color  distance
        self.color_dist = min(msg.ranges[8345:8365]) 
        #distance limits
        lim_sup_dist =  25
        lim_inf_dist = 0.30
          
        print(self.color_dist)
       
        if(self.flag):    
            
            if (self.color_dist  > lim_inf_dist and self.color_dist  < lim_sup_dist):
            
                if (self.robot_vel.linear.x < 0.5):
                    self.robot_vel.linear.x = self.robot_vel.linear.x + 0.1
                    
                elif(self.color_dist  > 0.50 and self.robot_vel.linear.x > 1):
                    self.robot_vel.linear.x = self.robot_vel.linear.x - 0.1
                    
                else:
                    self.robot_vel.linear.x = klinear * self.color_dist
                
            else:
                self.robot_vel.linear.x = 0
               
      
        
        
        
       
    def cleanup(self): 
        print('apagando motor')
        self.robot_vel.angular.z = 0
        self.robot_vel.linear.x = 0
      
       
        
############################### MAIN PROGRAM ####################################  
if __name__ == "__main__":  

    rospy.init_node("total_controller", anonymous=True)  
    TotalControlClass()

