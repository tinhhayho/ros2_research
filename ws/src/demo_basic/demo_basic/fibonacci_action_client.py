#!/usr/bin/env python3
"""Demo 1 — action client: sends a Fibonacci goal, prints each feedback + the result.

Exits non-zero unless it saw a result AND at least one feedback, so it doubles as a check.
"""
import sys
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from example_interfaces.action import Fibonacci


class FibonacciActionClient(Node):
    def __init__(self):
        super().__init__('fibonacci_action_client')
        self._client = ActionClient(self, Fibonacci, 'fibonacci')
        self.feedback_count = 0
        self.result = None

    def send(self, order):
        self._client.wait_for_server()
        goal = Fibonacci.Goal()
        goal.order = order
        fut = self._client.send_goal_async(goal, feedback_callback=self._on_feedback)
        rclpy.spin_until_future_complete(self, fut)
        goal_handle = fut.result()
        if not goal_handle.accepted:
            self.get_logger().error('goal rejected')
            return
        result_fut = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_fut)
        self.result = list(result_fut.result().result.sequence)
        self.get_logger().info(f'result: {self.result}')

    def _on_feedback(self, fb):
        self.feedback_count += 1
        self.get_logger().info(f'feedback: {list(fb.feedback.sequence)}')


def main(args=None):
    rclpy.init(args=args)
    node = FibonacciActionClient()
    node.send(5)
    ok = node.result is not None and node.feedback_count >= 1
    node.destroy_node()
    rclpy.try_shutdown()
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
