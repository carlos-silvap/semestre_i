#!/usr/bin/env python

import rospy
import time
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
        #self.cmd_vel_pub=rospy.Publisher("cmd_vel", Twist, queue_size = 1)
        self.cmd_vel_pub = rospy.Publisher('tracker_follow', Twist, queue_size=1)
        
        ### CONSTANTS ###
        self.robot_vel = Twist()
        self.robot_vel.angular.z = 0
        self.robot_vel.linear.x = 0
        r = rospy.Rate(10) #10 Hz       
        self.prev=0
        self.count=0
        self.cb=0
        self.flag = False
        self.time = time.time()
        
        ### INIT NODE ####  
        while not rospy.is_shutdown():
            print (self.robot_vel)
            
            if self.time-self.cb < 2: 
                print self.robot_vel
                self.cmd_vel_pub.publish(self.robot_vel)
            
            r.sleep()
            
    def radius_cb(self, msg):  
        self.cb = time.time() 
        klinear = 30
        self.rad = msg.data
            
     
        if ( 175 > self.rad > 50):
            self.robot_vel.linear.x = 0
            print("cerca")
            if (self.rad!=self.prev):
                self.count=0 
                 
        elif (self.rad > 175):
            self.robot_vel.linear.x = -0.1
            print("muy cerca")
            if (self.rad!=self.prev):
                self.count=0  
        
        else:   
            self.robot_vel.linear.x = klinear / (self.rad + 0.00001)
            
            if (self.rad!=self.prev):
                self.count=0 
        if (self.rad==self.prev and self.flag == True):
            self.count=self.count+1 
            if(self.count>10):
                self.robot_vel.linear.x=0
        
      
        self.prev = self.rad               
        print (self.count)
      
        
        
    def center_cb(self, msg):  
        kangular = 0.01
        self.center_x = msg.x
        self.x0 = 300
        self.xdiff = self.x0 - self.center_x
       
        self.robot_vel.angular.z = kangular*self.xdiff
        
        if (self.robot_vel.angular.z < 0.5):
            self.flag = True
        else:
            self.flag = False
        
        
       
    def cleanup(self): 
        print('apagando motor')
        self.robot_vel.angular.z = 0
        self.robot_vel.linear.x = 0
      
       
        
############################### MAIN PROGRAM ####################################  
if __name__ == "__main__":  

    rospy.init_node("color_velocity_controller", anonymous=True)  
    ColorVelControl() 

