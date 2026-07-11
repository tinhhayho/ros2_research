from setuptools import find_packages, setup

package_name = 'demo_basic'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/demo_basic.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='tinh',
    maintainer_email='tinhhayho@gmail.com',
    description='Demo 1: pub/sub + service + action in rclpy (teaching code).',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'talker = demo_basic.talker:main',
            'listener = demo_basic.listener:main',
            'add_two_ints_server = demo_basic.add_two_ints_server:main',
            'add_two_ints_client = demo_basic.add_two_ints_client:main',
            'fibonacci_action_server = demo_basic.fibonacci_action_server:main',
            'fibonacci_action_client = demo_basic.fibonacci_action_client:main',
        ],
    },
)
