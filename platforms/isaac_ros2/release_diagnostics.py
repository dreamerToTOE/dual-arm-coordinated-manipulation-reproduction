"""[ENGINEERING] 只在释放窗口记录同一步物体/工具/碰撞接触；不是吸盘力估计器。"""
import json
import math

TASK_IDS = ('task27_plus_outer', 'task27_minus_outer', 'task27_plus_inner',
            'task27_minus_inner', 'task27_center_insert')
ACTIVE_PHASES = {'SIDE_PRESS_ENTER', 'SIDE_PRESS_SETTLED', 'RELEASE_REQUEST',
                 'RELEASE_OPEN', 'RELEASE_HOLD_DONE', 'CLEARANCE_ENTER'}


def active_cube_index(phase):
    parts = phase.split(':')
    if len(parts) != 2 or parts[0] not in TASK_IDS or parts[1] not in ACTIVE_PHASES:
        return None
    return TASK_IDS.index(parts[0])


def tcp_from_link8(position, quaternion, offset, tool_quaternion):
    """输入全部来自同一步link8刚体与既有固定工具变换，不读USD显示矩阵。"""
    if not all(math.isfinite(v) for v in (*position, *quaternion, *offset, *tool_quaternion)):
        raise ValueError('Nonfinite tool transform')
    norm = math.hypot(*quaternion)
    if norm < 1e-12:
        raise ValueError('Invalid link quaternion')
    x, y, z, w = (v/norm for v in quaternion)
    rotation = ((1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)),
                (2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)),
                (2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)))
    p = [position[i]+sum(rotation[i][j]*offset[j] for j in range(3)) for i in range(3)]
    bx, by, bz, bw = tool_quaternion
    q = [w*bx+bw*x+y*bz-z*by, w*by+bw*y+z*bx-x*bz,
         w*bz+bw*z+x*by-y*bx, w*bw-x*bx-y*by-z*bz]
    qnorm = math.hypot(*q)
    if qnorm < 1e-12:
        raise ValueError('Invalid fixed tool quaternion')
    return {'position_m': p, 'quaternion_xyzw': [v/qnorm for v in q]}


class ReleaseDiagnostics:
    def __init__(self, node, sim_view, cube_paths, scene_values, stream,
                 phase_topic='/task01/release_phase', phase_index=active_cube_index):
        from isaacsim.core.prims import RigidPrim
        from physics_object_sampler import PhysicsObjectSampler
        from physics_contact_sampler import PhysicsContactSampler
        from rclpy.qos import QoSProfile, DurabilityPolicy
        from std_msgs.msg import String
        self.phase = ''
        self.stream = stream
        self.count = 0
        self.scene_values = scene_values
        self.phase_index = phase_index
        self.subscription = node.create_subscription(
            String, phase_topic, self._phase,
            QoSProfile(depth=10, durability=DurabilityPolicy.TRANSIENT_LOCAL))
        link_paths = [f'/World/{side}_fr3/fr3_link8' for side in ('left', 'right')]
        self.tool_view = RigidPrim(link_paths, reset_xform_properties=False,
                                   prepare_contact_sensors=False)
        self.tool_view.initialize()
        self.tool_sampler = PhysicsObjectSampler(self.tool_view)
        self.tool_sampler.capture()  # 启动时验证真实物理句柄，不能等发命令后才发现。
        self.articulations = {side: sim_view.create_articulation_view(f'/World/{side}_fr3')
                              for side in ('left', 'right')}
        fixed = ['/World/Table'] + [f'/World/Task27/TruckBox/{name}' for name in
                                    ('WallDeep', 'WallMinusY', 'WallPlusY')] + link_paths
        self.contacts = []
        for path in cube_paths:
            filters = fixed + [other for other in cube_paths if other != path]
            contact_view = sim_view.create_rigid_contact_view(path, filters, 256)
            if not contact_view.check():
                raise RuntimeError('Contact view is invalid before robot commands')
            self.contacts.append(PhysicsContactSampler(contact_view, [path], filters))

    def _phase(self, message):
        self.phase = message.data

    def capture(self, cube_snapshot, dt, grippers):
        phase = self.phase
        index = self.phase_index(phase)
        if index is None:
            return
        from dataclasses import asdict
        import numpy as np
        tools = self.tool_sampler.capture()
        if (tools.stamp_ns, tools.physics_step) != (cube_snapshot.stamp_ns, cube_snapshot.physics_step):
            raise RuntimeError('Cube/tool observations do not share the same physics step')
        tcps = {}
        for side, body in zip(('left', 'right'), tools.bodies):
            sign = self.scene_values['branch_sign'][side]
            tcps[side] = tcp_from_link8(body.position_m, body.quaternion_xyzw,
                (0.0, sign*self.scene_values['tcp_y'], self.scene_values['vertical_drop_z']),
                (0.0, 0.0, sign*2**-.5, 2**-.5))
        row = {'physics': asdict(cube_snapshot), 'tools_physics': asdict(tools),
               'tcp_poses_world_from_physics_link8': tcps,
               'collision_contacts': self.contacts[index].capture(cube_snapshot, dt),
               'joint_positions_rad': {side: np.asarray(art.get_dof_positions()).tolist()
                                       for side, art in self.articulations.items()},
               'phase_received_async': phase,
               'suction_closed': {side: bool(g.is_closed()) for side, g in grippers.items()}}
        if self.stream is not None:
            self.stream.write(json.dumps(row, sort_keys=True)+'\n')
        self.count += 1
        return row
