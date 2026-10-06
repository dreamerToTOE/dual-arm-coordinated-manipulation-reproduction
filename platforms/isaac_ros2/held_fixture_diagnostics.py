"""[ENGINEERING] 新3+2持件窗口同一步只读观测；不控制、不估算TCP力。"""
import json
import re
import numpy as np
from release_diagnostics import ReleaseDiagnostics, TASK_IDS


def held_cube_index(phase):
    parts = phase.split(':')
    if len(parts) != 2 or parts[0] not in TASK_IDS[:3]:
        return None
    if parts[1] in ('CONTACT', 'ROLE_SWAP', 'ABORT', 'COMPLETE') or re.fullmatch(
            r'(X|Y)_(?:[1-9]|1[0-6])', parts[1]):
        return TASK_IDS.index(parts[0])
    return None


def finite_vector(value, expected):
    result = np.asarray(value, dtype=float).reshape(-1)
    if len(result) != expected or not np.isfinite(result).all():
        raise ValueError('Invalid articulation vector or DOF mapping')
    return result.tolist()


class HeldFixtureDiagnostics(ReleaseDiagnostics):
    def __init__(self, node, sim_view, cube_paths, scene_values, stream):
        super().__init__(node, sim_view, cube_paths, scene_values, None,
                         '/task01/fixture_phase', held_cube_index)
        from isaacsim.core.prims import RigidPrim
        from physics_object_sampler import PhysicsObjectSampler
        from physics_contact_sampler import PhysicsContactSampler
        self.output = stream
        self.names = {side: list(view.get_metatype(0).dof_names)
                      for side, view in self.articulations.items()}
        self.robot_paths = [path for view in self.articulations.values()
                            for path in view.link_paths[0]]
        if len(set(self.robot_paths)) != len(self.robot_paths):
            raise ValueError('Duplicate articulation body paths')
        robot_view = RigidPrim(self.robot_paths, reset_xform_properties=False,
                               prepare_contact_sensors=False)
        robot_view.initialize()
        self.robot_sampler = PhysicsObjectSampler(robot_view)
        self.robot_sampler.capture()
        filters = ['/World/Table'] + [f'/World/Task27/TruckBox/{name}' for name in
                                     ('WallDeep', 'WallMinusY', 'WallPlusY')]
        self.filters = filters + list(cube_paths) + self.robot_paths
        view = sim_view.create_rigid_contact_view(
            self.robot_paths, [self.filters for _ in self.robot_paths], 4096)
        self.robot_contacts = PhysicsContactSampler(view, self.robot_paths, self.filters)
        # 启动前验证力矩API/DOF次序；拒绝力与力矩混用的fallback。
        self.articulation_state()

    def articulation_state(self):
        result = {}
        for side, view in self.articulations.items():
            size = len(self.names[side])
            result[side] = {'dof_names': self.names[side],
                'positions_rad': finite_vector(view.get_dof_positions(), size),
                'velocities_rad_s': finite_vector(view.get_dof_velocities(), size),
                'position_targets_rad': finite_vector(view.get_dof_position_targets(), size),
                'projected_joint_effort_raw': finite_vector(view.get_dof_projected_joint_forces(), size),
                'actuation_effort_raw': finite_vector(view.get_dof_actuation_forces(), size)}
        return result

    def capture(self, cube_snapshot, dt, grippers):
        if held_cube_index(self.phase) is None:
            return
        row = super().capture(cube_snapshot, dt, grippers)
        from dataclasses import asdict
        robots = self.robot_sampler.capture()
        if (robots.stamp_ns, robots.physics_step) != (cube_snapshot.stamp_ns, cube_snapshot.physics_step):
            raise RuntimeError('Robot/Cube snapshots must share one physics step')
        row['robots_physics'] = asdict(robots)
        row['robot_collision_contacts'] = self.robot_contacts.capture(robots, dt, nonzero_only=True)
        row['articulations'] = self.articulation_state()
        row['effort_source'] = ('get_dof_projected_joint_forces; revolute DOFs Nm, '
            'finger prismatic DOFs N; raw/NOT calibrated TCP wrench')
        self.output.write(json.dumps(row, sort_keys=True)+'\n')

    def topology(self):
        return {'dof_names': self.names, 'robot_sensor_paths': self.robot_paths,
                'robot_filter_paths': self.filters, 'max_robot_contact_data_count': 4096,
                'boundary': 'Collision contacts omit suction D6 constraint loads; phase labels asynchronous'}
