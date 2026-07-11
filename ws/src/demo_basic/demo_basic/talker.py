#!/usr/bin/env python3
"""Demo 1 — minimal rclpy publisher ("talker").

Firmware analogy: a node appearing on the ROS 2 graph is like a device enumerating on a
shared bus — no master assigns it an address, discovery is automatic. This talker just
publishes a counter string on /chatter at 2 Hz.
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Talker(Node):
    def __init__(self):
        super().__init__('talker')                          # name shown in `ros2 node list`
        self.pub = self.create_publisher(String, 'chatter', 10)  # topic, queue depth 10
        self.timer = self.create_timer(0.5, self.tick)      # 2 Hz
        self.count = 0
        self.get_logger().info('talker up: publishing on /chatter')

    def tick(self):
        msg = String()
        msg.data = f'Hello ROS 2 (rclpy): {self.count}'
        self.pub.publish(msg)
        self.get_logger().info(f'pub: "{msg.data}"')
        self.count += 1


def main(args=None):
    rclpy.init(args=args)
    node = Talker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
