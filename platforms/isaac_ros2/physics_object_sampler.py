"""Isaac 4.5 measurement adapter: one post-step physics snapshot, one sim stamp.

[ENGINEERING] TASK01 calibration support. This is not a frozen TASK02 interface.
The caller owns the initialized RigidPrim view and the ROS node. Neither sampling
nor publishing sets robot targets, changes scene transforms, or reads USD poses.
"""

from dataclasses import asdict, dataclass
import json
import math


@dataclass(frozen=True)
class BodySample:
    prim_path: str
    position_m: tuple
    quaternion_xyzw: tuple
    linear_velocity_m_s: tuple
    angular_velocity_rad_s: tuple


@dataclass(frozen=True)
class PhysicsSnapshot:
    stamp_ns: int
    physics_step: int
    frame_id: str
    bodies: tuple


class PhysicsObjectSampler:
    def __init__(self, rigid_view, frame_id="world"):
        from isaacsim.core.nodes.bindings import _isaacsim_core_nodes
        self.view = rigid_view
        self.frame_id = frame_id
        self.core = _isaacsim_core_nodes.acquire_interface()
        self.paths = tuple(rigid_view.prim_paths)
        self.last_stamp_ns = None

    def capture(self):
        # Handle loss must fail explicitly: RigidPrim otherwise falls back to USD.
        if not self.view.is_physics_handle_valid():
            raise RuntimeError("No live physics handle; refusing USD fallback")
        positions, wxyz = self.view.get_world_poses(clone=True)
        linear = self.view.get_linear_velocities(clone=True)
        angular = self.view.get_angular_velocities(clone=True)
        stamp_ns = round(float(self.core.get_sim_time()) * 1e9)
        physics_step = int(self.core.get_physics_num_steps())
        if self.last_stamp_ns is not None and stamp_ns <= self.last_stamp_ns:
            raise RuntimeError("Simulation stamp did not advance; start a new sampler after reset")
        bodies = []
        for index, path in enumerate(self.paths):
            quaternion = tuple(float(wxyz[index][i]) for i in (1, 2, 3, 0))
            norm = math.sqrt(sum(value * value for value in quaternion))
            if norm < 1e-12 or not math.isfinite(norm):
                raise ValueError(f"Invalid physics quaternion for {path}")
            values = tuple(float(v) for v in positions[index])
            lv = tuple(float(v) for v in linear[index])
            av = tuple(float(v) for v in angular[index])
            if not all(math.isfinite(v) for v in values + lv + av):
                raise ValueError(f"Nonfinite physics state for {path}")
            bodies.append(BodySample(path, values, tuple(v / norm for v in quaternion), lv, av))
        self.last_stamp_ns = stamp_ns
        return PhysicsSnapshot(stamp_ns, physics_step, self.frame_id, tuple(bodies))


class PhysicsPosePublisher:
    def __init__(self, node, sampler, topic="/task01/physics/cube_poses"):
        import omni.physx
        from geometry_msgs.msg import PoseArray
        from std_msgs.msg import String
        self.node, self.sampler = node, sampler
        self.pose_pub = node.create_publisher(PoseArray, topic, 100)
        self.snapshot_pub = node.create_publisher(String, topic + "/snapshot", 100)
        self.errors, self.snapshots = [], 0
        self.latest = None
        self.subscription = omni.physx.get_physx_interface().subscribe_physics_on_step_events(
            self._post_step, False, 200)

    def _post_step(self, dt):
        from geometry_msgs.msg import Pose, PoseArray
        from std_msgs.msg import String
        try:
            sample = self.sampler.capture()
            message = PoseArray()
            message.header.frame_id = sample.frame_id
            message.header.stamp.sec = sample.stamp_ns // 1_000_000_000
            message.header.stamp.nanosec = sample.stamp_ns % 1_000_000_000
            for body in sample.bodies:
                pose = Pose()
                pose.position.x, pose.position.y, pose.position.z = body.position_m
                (pose.orientation.x, pose.orientation.y,
                 pose.orientation.z, pose.orientation.w) = body.quaternion_xyzw
                message.poses.append(pose)
            self.pose_pub.publish(message)
            info = String()
            info.data = json.dumps(asdict(sample), sort_keys=True)
            self.snapshot_pub.publish(info)
            self.latest = sample
            self.snapshots += 1
        except Exception as error:
            self.errors.append(repr(error))
            if len(self.errors) <= 3:
                self.node.get_logger().error(f"Physics snapshot failed: {error}")

    def close(self):
        if self.subscription is not None:
            self.subscription.unsubscribe()
            self.subscription = None
