#!/usr/bin/env python3
"""Demo 2 — configurable-QoS publisher.

Publishes an incrementing "qos msg N" string. Reliability/durability/depth come from
ROS params so the matrix runner can pair it against subscribers of every QoS combo.
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from demo_qos.qos_common import declare_qos


class QosPub(Node):
    def __init__(self):
        super().__init__('qos_pub')
        topic = self.declare_parameter('topic', 'qos_chatter').value
        rate = self.declare_parameter('rate_hz', 5.0).value
        qos, rel, dur, depth = declare_qos(self)
        self.pub = self.create_publisher(String, topic, qos)
        self.count = 0
        self.create_timer(1.0 / rate, self.tick)
        self.get_logger().info(
            f'qos_pub on /{topic}: reliability={rel} durability={dur} depth={depth}')

    def tick(self):
        msg = String()
        msg.data = f'qos msg {self.count}'
        self.pub.publish(msg)
        self.count += 1


def main(args=None):
    rclpy.init(args=args)
    node = QosPub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
