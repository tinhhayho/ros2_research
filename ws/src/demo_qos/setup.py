from setuptools import find_packages, setup

package_name = 'demo_qos'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='tinh',
    maintainer_email='tinhhayho@gmail.com',
    description='Demo 2: QoS compatibility — configurable pub/sub for the RxO matrix.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'qos_pub = demo_qos.qos_pub:main',
            'qos_sub = demo_qos.qos_sub:main',
        ],
    },
)
