#!/usr/bin/env python3
"""Demo 1 — service server for example_interfaces/srv/AddTwoInts.

Service = request/response (synchronous RPC), vs a topic = fire-and-forget stream.
Firmware analogy: a service call is like a register read/write transaction that returns a
value; a topic is like a periodic broadcast frame nobody acknowledges.
"""
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class AddTwoIntsServer(Node):
    def __init__(self):
        super().__init__('add_two_ints_server')
        # NB: don't name this callback `handle` — rclpy.Node has a `handle` property
        # and a method of the same name shadows it, breaking Node.__init__.
        self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.on_request)
        self.get_logger().info('service ready: /add_two_ints')

    def on_request(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'{request.a} + {request.b} = {response.sum}')
        return response


def main(args=None):
    rclpy.init(args=args)
    node = AddTwoIntsServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
