"""Demo 1 launch — brings up the whole graph as SEPARATE processes.

talker (rclpy) + talker_cpp (rclcpp) both publish /chatter; listener subscribes; plus the
service and action servers. The nodes discover each other with no master and no central
broker — that's the core point. The two talkers (Python + C++) on one topic show language
interop on a single bus.
"""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='demo_basic', executable='talker', name='talker', output='screen'),
        Node(package='demo_basic_cpp', executable='talker_cpp', name='talker_cpp', output='screen'),
        Node(package='demo_basic', executable='listener', name='listener', output='screen'),
        Node(package='demo_basic', executable='add_two_ints_server',
             name='add_two_ints_server', output='screen'),
        Node(package='demo_basic', executable='fibonacci_action_server',
             name='fibonacci_action_server', output='screen'),
    ])
