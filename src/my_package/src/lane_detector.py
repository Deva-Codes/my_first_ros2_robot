import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np
import math

class LaneDetector(Node):
    def __init__(self):
        super().__init__('lane_detector')
        self.bridge = CvBridge()
        
        # Subscribe to camera, Publish to cmd_vel
        self.subscription = self.create_subscription(Image, '/camera/image', self.camera_callback, 10)
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Proportional gain for our steering controller
        self.kp = 0.01
        
        self.get_logger().info("IGVC Lane Detector Node Started.")

    def camera_callback(self, msg):
        # 1. Convert ROS Image to OpenCV BGR array
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        height, width, _ = cv_image.shape

        # 2. Convert to HSV and create the White Mask
        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        lower_white = np.array([0, 0, 110])
        upper_white = np.array([0, 0, 255])
        mask = cv2.inRange(hsv_image, lower_white, upper_white)

        # 3. Blur and Edge Detection
        blurred = cv2.GaussianBlur(mask, (5, 5), 0)
        edges = cv2.Canny(blurred, 30, 150)

        # 4. Region of Interest (ROI) Slicing
        # We only want to look at the bottom half of the image
        roi = edges[height//2:height, 0:width]

        # 5. Hough Line Transform
        # Finds straight lines in the binary edge image
        lines = cv2.HoughLinesP(
            roi, 
            rho=1, 
            theta=np.pi/180, 
            threshold=20, 
            minLineLength=10, 
            maxLineGap=50
        )

        # 6. Calculate Lane Center
        lane_center = width // 2  # Default to straight ahead
        
        if lines is not None:
            left_x = []
            right_x = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if x1<width//2:
                    left_x.extend([x1])
                else:
                    right_x.extend([x1])
                if x2<width//2:
                    left_x.extend([x2])
                else:
                    right_x.extend([x2])
                
                
                
                # Draw the detected lines in green on our debug GUI
                # We add height//2 to Y because the lines were found in the cropped ROI
                cv2.line(cv_image, (x1, y1 + height//2), (x2, y2 + height//2), (0, 255, 0), 2)

            if len(right_x)  > 0 or len(left_x) >0:
                # The approximate center of the lane is the average of all detected line X-coordinates
                lane_center = int((np.mean(right_x)+np.mean(left_x))//2)
                
                # Draw a red dot at the calculated lane center
                cv2.circle(cv_image, (lane_center, height - 50), 10, (0, 0, 255), -1)

        # 7. Steering Controller Math
        image_center = width // 2
        error = image_center - lane_center

        cmd = Twist()
        cmd.linear.x = 3.0  # Constant forward speed of 0.5 m/s
        cmd.angular.z = float(self.kp * error)
        self.publisher_.publish(cmd)

        # 8. IGVC Required Debug GUI
        cv2.imshow("IGVC Vision - Lane Lines", cv_image)
        cv2.imshow("binary mask" , mask)
        cv2.imshow("blurred",blurred)
        cv2.imshow("canny mask" , edges)

        cv2.waitKey(1) # Required for OpenCV to actually render the window

def main():
    rclpy.init()
    node = LaneDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()