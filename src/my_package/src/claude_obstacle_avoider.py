import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class ObstacleAvoider(Node):
    def __init__(self):
        super().__init__('obstacle_avoider')

        # Subscribe to the LiDAR scan topic
        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)

        # Publish velocity commands to the diff drive controller
        self.publisher = self.create_publisher(
            Twist, '/diff_drive_controller/cmd_vel', 10)

        self.get_logger().info('Obstacle Avoider node started')

    def angle_to_index(self, angle_rad, angle_min, angle_increment):
        return int((angle_rad - angle_min) / angle_increment)

    def scan_callback(self, msg):
        angle_min = msg.angle_min
        angle_increment = msg.angle_increment
        ranges = msg.ranges

        # Define front, left, and right sectors (in degrees, converted to radians)
        front_start = self.angle_to_index(math.radians(-20), angle_min, angle_increment)
        front_end = self.angle_to_index(math.radians(20), angle_min, angle_increment)

        left_start = self.angle_to_index(math.radians(20), angle_min, angle_increment)
        left_end = self.angle_to_index(math.radians(60), angle_min, angle_increment)

        right_start = self.angle_to_index(math.radians(-60), angle_min, angle_increment)
        right_end = self.angle_to_index(math.radians(-20), angle_min, angle_increment)

        front_indices = range(max(0, front_start), min(len(ranges), front_end))
        left_indices = range(max(0, left_start), min(len(ranges), left_end))
        right_indices = range(max(0, right_start), min(len(ranges), right_end))

        # Get minimum distance in each sector, ignoring inf (no detection) values
        front_min = min(
            (ranges[i] for i in front_indices if not math.isinf(ranges[i])),
            default=999.0)
        left_min = min(
            (ranges[i] for i in left_indices if not math.isinf(ranges[i])),
            default=999.0)
        right_min = min(
            (ranges[i] for i in right_indices if not math.isinf(ranges[i])),
            default=999.0)

        cmd = Twist()
        SAFE_DISTANCE = 1.0

        if front_min < SAFE_DISTANCE:
            # Obstacle ahead - slow down and steer toward the side with more room
            cmd.linear.x = 0.2
            if left_min > right_min:
                cmd.angular.z = 0.5    # more room on the left -> turn left
            else:
                cmd.angular.z = -0.5   # more room on the right -> turn right
            self.get_logger().info(
                f'Obstacle at {front_min:.2f}m - avoiding (left={left_min:.2f}, right={right_min:.2f})')
        else:
            # Path clear - cruise straight ahead
            cmd.linear.x = 0.5
            cmd.angular.z = 0.0

        self.publisher.publish(cmd)


def main():
    rclpy.init()
    node = ObstacleAvoider()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()