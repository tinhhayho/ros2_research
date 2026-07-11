#!/usr/bin/env python3
"""Demo 1 — minimal rclpy subscriber ("listener").

Subscribes /chatter. Because BOTH the rclpy talker and the rclcpp talker_cpp publish on
the same topic, this one listener receives from both — many-to-one, no central broker,
no master. That is the core ROS 2 "aha" for an embedded audience used to point-to-point links.
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Listener(Node):
    def __init__(self):
        super().__init__('listener')
        self.sub = self.create_subscription(String, 'chatter', self.on_msg, 10)
        self.get_logger().info('listener up: subscribed to /chatter')

    def on_msg(self, msg):
        self.get_logger().info(f'recv: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    node = Listener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
