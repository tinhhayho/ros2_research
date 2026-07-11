#!/usr/bin/env python3
"""Demo 1 — action server for example_interfaces/action/Fibonacci.

Action = a long-running goal with feedback + result + cancel (vs a one-shot service).
Firmware analogy: like kicking off a DMA transfer or a motor move — you get progress
updates (feedback) as it runs, can cancel midway, and finally get a completion (result).
"""
import time
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from example_interfaces.action import Fibonacci


class FibonacciActionServer(Node):
    def __init__(self):
        super().__init__('fibonacci_action_server')
        self._srv = ActionServer(self, Fibonacci, 'fibonacci', self.execute)
        self.get_logger().info('action server ready: /fibonacci')

    def execute(self, goal_handle):
        order = goal_handle.request.order
        self.get_logger().info(f'goal accepted: order={order}')
        sequence = [0, 1]
        feedback = Fibonacci.Feedback()
        for i in range(1, order):
            sequence.append(sequence[i] + sequence[i - 1])
            feedback.sequence = sequence
            goal_handle.publish_feedback(feedback)      # one progress update per step
            self.get_logger().info(f'feedback: {sequence}')
            time.sleep(0.3)
        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = sequence
        self.get_logger().info(f'result: {sequence}')
        return result


def main(args=None):
    rclpy.init(args=args)
    node = FibonacciActionServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
