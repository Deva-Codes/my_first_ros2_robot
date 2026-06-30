import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix,Imu
from geometry_msgs.msg import Twist

class GpsWaypointFollower(Node):
    def __init__(self):
        super().__init__('gps_waypoint_follower')

        self.current_lat = None
        self.current_lon = None
        self.current_yaw = None

        self.target_lat = 0.000090
        self.target_lon = 0.000000

        self.create_subscription(NavSatFix,'/navsat',self.gps_callback,10)
        self.create_subscription(Imu,'/imu',self.imu_callback,10)
        self.publisher  = self.create_publisher(Twist,'/cmd_vel',10)

        self.timer = self.create_timer(0.1,self.control_loop)
        self.get_logger().info("gps waypoint navigator started")

    def gps_callback(self,msg):
        self.current_lat = msg.latitude
        self.current_lon = msg.longitude

    def imu_callback(self,msg):
        q = msg.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.current_yaw = math.atan2(siny_cosp, cosy_cosp)
    def control_loop(self):
        if self.current_lat == None or self.current_yaw is None:
            return
        delta_lat = self.target_lat - self.current_lat
        delta_lon = self.target_lon - self.current_lon

        meters_north = delta_lat *111320
        meters_east = delta_lon *111320 *math.cos(math.radians(self.current_lat))

        distance = math.sqrt(meters_north**2 + meters_east**2)

        bearing = math.atan2(meters_east,meters_north)

        heading_error = bearing-self.current_yaw

        heading_error = math.atan2(math.sin(heading_error), math.cos(heading_error))
        
        cmd = Twist()
        if(distance<1.0):
            cmd.linear.x = 0.0
            cmd.angular.z =0.0
            self.get_logger().info('waypoint reached')
        else:
            cmd.linear.x =0.5
            cmd.angular.z = 1.5 *heading_error
            self.get_logger().info(f'dist={distance:.2f}m bearing_err={math.degrees(heading_error):.1f}deg')
        self.publisher.publish(cmd)

def main():
    rclpy.init()
    node = GpsWaypointFollower()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()

    