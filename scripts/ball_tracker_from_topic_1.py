#!/usr/bin/env python
""" This program publishes a given integer to a ROS topic
    published topic:
        /number_topic
"""
# import ROS stuff
import rospy
from std_msgs.msg import Int32
from geometry_msgs.msg import Point
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import rospy



# construct the argument parse and parse the arguments
class BallTracker():
    def __init__(self):
        # Init the ros node
        rospy.init_node("ball_tracker")
        self.pub_center = rospy.Publisher('center', Point, queue_size=10)
        self.pub_radius = rospy.Publisher('radius', Int32, queue_size=10)
        self.image_sub = rospy.Subscriber("/uma_robot/camera1/image_raw",Image,self.camera_callback)
        self.bridge_object = CvBridge() #Creates the bridge object between ROS and opencv images
        self.center_ros = Point()
        self.radius_ros=0

        ap = argparse.ArgumentParser()
        ap.add_argument("-v", "--video",
            help="path to the (optional) video file")
        ap.add_argument("-b", "--buffer", type=int, default=64,
            help="max buffer size")
        self.args = vars(ap.parse_args())


        # define the lower and upper boundaries of the "green"
        # ball in the HSV color space, then initialize the
        # list of tracked points
        self.greenLower = (112, 197, 26)
        self.greenUpper = (137, 243, 40)
        #self.greenLower = (5, 50, 50)
        #self.greenUpper = (15, 255, 255)
        self.pts = deque(maxlen=self.args["buffer"])


        #To adjust the execution rate of the while Loop
        ros_rate = rospy.Rate(10) #10Hz
        # keep looping
        while not rospy.is_shutdown():
            if self.radius_ros>0: #Just publish something if the radius is large enough
                self.pub_center.publish(self.center_ros)
                self.pub_radius.publish(self.radius_ros)
           
            ros_rate.sleep()

        # close all windows
        cv2.destroyAllWindows()

    def camera_callback(self, data):
        print("callback")
        try:
            # We select bgr8 because its the OpenCV encoding by default
            self.frame = self.bridge_object.imgmsg_to_cv2(data, desired_encoding="bgr8")
        except CvBridgeError as e:
            print(e)


        # resize the frame, blur it, and convert it to the HSV
        # color space
        self.frame = imutils.resize(self.frame, width=600)
        blurred = cv2.GaussianBlur(self.frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # construct a mask for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, self.greenLower, self.greenUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                self.center_ros.x=float(x)
                self.center_ros.y=float(y)
                self.center_ros.z=0 #As it is an image z is not used.
                self.radius_ros=int(radius)

                cv2.circle(self.frame, (int(x), int(y)), int(radius),
                    (0, 255, 255), 2)
                cv2.circle(self.frame, center, 5, (0, 0, 255), -1)

        # update the points queue
        self.pts.appendleft(center)

        # loop over the set of tracked points
        for i in range(1, len(self.pts)):
            # if either of the tracked points are None, ignore
            # them
            if self.pts[i - 1] is None or self.pts[i] is None:
                continue

            # otherwise, compute the thickness of the line and
            # draw the connecting lines
            thickness = int(np.sqrt(self.args["buffer"] / float(i + 1)) * 2.5)
            cv2.line(self.frame, self.pts[i - 1], self.pts[i], (0, 0, 255), thickness)

        # show the frame to our screen
        cv2.imshow("Frame", self.frame)
        key = cv2.waitKey(1) & 0xFF


if __name__ == '__main__':
    BallTracker()
