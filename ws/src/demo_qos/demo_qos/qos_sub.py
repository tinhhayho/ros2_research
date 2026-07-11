#!/usr/bin/env python3
"""Demo 2 — configurable-QoS subscriber.

Counts messages received over a fixed window, then prints a single machine-parseable line:
    RECEIVED:<count> FIRST:<first message data or None>
The matrix runner parses that to fill the compatibility table. FIRST is used by the
late-joiner case: a transient_local sub joining late sees an OLD (low-index) message first,
while a volatile sub sees only NEW ones.
"""
import rclpy
from rcl_interfaces.msg import ParameterDescriptor
from rclpy.node import Node
from std_msgs.msg import String

from demo_qos.qos_common import declare_qos


class QosSub(Node):
    def __init__(self):
        super().__init__('qos_sub')
        topic = self.declare_parameter('topic', 'qos_chatter').value
        # dynamic_typing so `run_seconds:=4` (int) and `:=4.0` (float) both work
        self.run_seconds = float(self.declare_parameter(
            'run_seconds', 4.0, ParameterDescriptor(dynamic_typing=True)).value)
        qos, rel, dur, depth = declare_qos(self)
        self.count = 0
        self.first = None
        self.done = False
        self.sub = self.create_subscription(String, topic, self.on_msg, qos)
        self.get_logger().info(
            f'qos_sub on /{topic}: reliability={rel} durability={dur} depth={depth}')
        self.create_timer(self.run_seconds, self._finish)

    def on_msg(self, msg):
        if self.first is None:
            self.first = msg.data
        self.count += 1

    def _finish(self):
        self.done = True


def main(args=None):
    rclpy.init(args=args)
    node = QosSub()
    while rclpy.ok() and not node.done:
        rclpy.spin_once(node, timeout_sec=0.1)
    node.get_logger().info(f'RECEIVED:{node.count} FIRST:{node.first}')
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
