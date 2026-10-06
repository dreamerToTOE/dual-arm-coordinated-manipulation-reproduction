"""[ENGINEERING] Cube + two fixed TCPs in one live-PhysX post-step message.

Only observations: never changes scene, grippers, robot targets or legacy topics.
Layout: existing cube_paths order, then left TCP, then right TCP, world/xyzw/SI.
"""
from dataclasses import asdict
import json
from physics_object_sampler import PhysicsObjectSampler
from release_diagnostics import tcp_from_link8

TOPIC = '/task01/physics/fixture_geometry'


def geometry_poses(snapshot, cube_paths, scene_values):
    paths = tuple(cube_paths)
    expected = paths + ('/World/left_fr3/fr3_link8', '/World/right_fr3/fr3_link8')
    if snapshot.frame_id != 'world' or tuple(b.prim_path for b in snapshot.bodies) != expected:
        raise ValueError('Unexpected fixture snapshot frame/path order')
    poses = [{'position_m': b.position_m, 'quaternion_xyzw': b.quaternion_xyzw}
             for b in snapshot.bodies[:len(paths)]]
    for side, body in zip(('left', 'right'), snapshot.bodies[len(paths):]):
        sign = scene_values['branch_sign'][side]
        poses.append(tcp_from_link8(body.position_m, body.quaternion_xyzw,
            (0.0, sign * scene_values['tcp_y'], scene_values['vertical_drop_z']),
            (0.0, 0.0, sign * 2**-.5, 2**-.5)))
    return poses


class FixtureGeometryPublisher:
    def __init__(self, bridge, cube_paths, scene_values, comparison_stream=None):
        import omni.physx
        from isaacsim.core.prims import RigidPrim
        from geometry_msgs.msg import PoseArray
        self.bridge, self.paths, self.values = bridge, tuple(cube_paths), scene_values
        self.comparison_stream = comparison_stream
        self.view = RigidPrim(list(self.paths) +
            ['/World/left_fr3/fr3_link8', '/World/right_fr3/fr3_link8'],
            reset_xform_properties=False, prepare_contact_sensors=False)
        self.view.initialize()
        self.sampler = PhysicsObjectSampler(self.view)
        geometry_poses(self.sampler.capture(), self.paths, self.values)
        self.publisher = bridge.node.create_publisher(PoseArray, TOPIC, 10)
        self.errors, self.snapshots = [], 0
        self.subscription = omni.physx.get_physx_interface().subscribe_physics_on_step_events(
            self._post_step, False, 200)

    def _post_step(self, dt):
        from geometry_msgs.msg import Pose, PoseArray
        try:
            snapshot = self.sampler.capture()
            poses = geometry_poses(snapshot, self.paths, self.values)
            message = PoseArray()
            message.header.frame_id = 'world'
            message.header.stamp.sec = snapshot.stamp_ns // 1_000_000_000
            message.header.stamp.nanosec = snapshot.stamp_ns % 1_000_000_000
            for data in poses:
                pose = Pose()
                pose.position.x, pose.position.y, pose.position.z = data['position_m']
                (pose.orientation.x, pose.orientation.y,
                 pose.orientation.z, pose.orientation.w) = data['quaternion_xyzw']
                message.poses.append(pose)
            self.publisher.publish(message)
            self.snapshots += 1
            # Same callback source comparison, not ROS delivery-time alignment.
            if self.comparison_stream is not None and self.snapshots % 3 == 0:
                old_paths = self.paths + tuple(
                    f'/World/{s}_fr3/fr3_link8/side_suction_tool/side_suction_tcp'
                    for s in ('left', 'right'))
                legacy = []
                for path in old_paths:
                    pose = self.bridge._pose(path)
                    legacy.append({'position_m': [pose.position.x, pose.position.y, pose.position.z],
                        'quaternion_xyzw': [pose.orientation.x, pose.orientation.y,
                                            pose.orientation.z, pose.orientation.w]})
                self.comparison_stream.write(json.dumps({
                    'physics': asdict(snapshot), 'atomic_poses': poses,
                    'legacy_usd_same_callback': legacy}, sort_keys=True) + '\n')
        except Exception as error:
            self.errors.append(repr(error))
            if len(self.errors) <= 3:
                self.bridge.node.get_logger().error(f'Atomic fixture feedback failed: {error}')

    def close(self):
        if self.subscription is not None:
            self.subscription.unsubscribe()
            self.subscription = None
        self.bridge.node.destroy_publisher(self.publisher)
