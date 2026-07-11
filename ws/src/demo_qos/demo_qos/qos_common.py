"""Shared QoS helpers for Demo 2: map string ROS params -> rclpy QoS policies.

Only reliability + durability + depth are exposed — enough to demonstrate the
Request-vs-Offered (RxO) compatibility rule. History/Lifespan are intentionally left
default because they do NOT affect compatibility (a common misconception, see docs/03).
"""
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

_REL = {
    'reliable': ReliabilityPolicy.RELIABLE,
    'best_effort': ReliabilityPolicy.BEST_EFFORT,
}
_DUR = {
    'volatile': DurabilityPolicy.VOLATILE,
    'transient_local': DurabilityPolicy.TRANSIENT_LOCAL,
}


def declare_qos(node):
    """Declare reliability/durability/depth params and return (QoSProfile, rel, dur, depth)."""
    rel = node.declare_parameter('reliability', 'reliable').value
    dur = node.declare_parameter('durability', 'volatile').value
    depth = node.declare_parameter('depth', 10).value
    qos = QoSProfile(depth=depth)
    qos.reliability = _REL[rel]
    qos.durability = _DUR[dur]
    return qos, rel, dur, depth
