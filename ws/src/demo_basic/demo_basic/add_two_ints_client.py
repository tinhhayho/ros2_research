#!/usr/bin/env python3
"""Demo 1 — service client: calls add_two_ints(2, 3) once, prints the result, exits.

Exits non-zero if the math is wrong, so it doubles as a scripted check.
"""
import sys
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class AddTwoIntsClient(Node):
    def __init__(self):
        super().__init__('add_two_ints_client')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('waiting for /add_two_ints ...')

    def call(self, a, b):
        req = AddTwoInts.Request()
        req.a, req.b = a, b
        future = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        return future.result().sum


def main(args=None):
    rclpy.init(args=args)
    node = AddTwoIntsClient()
    a, b = 2, 3
    result = node.call(a, b)
    node.get_logger().info(f'{a} + {b} = {result}')
    node.destroy_node()
    rclpy.try_shutdown()
    sys.exit(0 if result == a + b else 1)


if __name__ == '__main__':
    main()
