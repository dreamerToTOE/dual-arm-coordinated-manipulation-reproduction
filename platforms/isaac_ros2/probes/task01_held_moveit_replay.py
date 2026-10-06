"""[ENGINEERING] 记录实测/命令关节的只读 FK/状态有效性服务重放。

不创建 joint/suction/feed/rail publisher，也不修改远程 PlanningScene/ACM。
阶段标签异步；仅被选行的 pose/contact/DOF 是同一个 post-step。
"""
import argparse
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET


def select_steps(stream, steps):
    selected = {}
    for line in stream:
        row = json.loads(line)
        step = row['physics']['physics_step']
        if step in steps:
            if step in selected:
                raise ValueError('Repeated selected step')
            selected[step] = row
    if set(selected) != set(steps):
        raise ValueError('Missing selected physics step')
    return [selected[step] for step in steps]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stream', type=Path)
    parser.add_argument('--steps', type=int, nargs='+', required=True)
    parser.add_argument('--rail-shift-x', type=float, required=True)
    args = parser.parse_args()
    if not math.isfinite(args.rail_shift_x) or len(set(args.steps)) != len(args.steps):
        parser.error('Finite known rail shift / distinct exact steps required')
    with args.stream.open() as source:
        selected = select_steps(source, args.steps)
    import rclpy
    from moveit_msgs.srv import GetPositionFK, GetStateValidity, GetPlanningScene
    from moveit_msgs.msg import PlanningSceneComponents, RobotState
    from rcl_interfaces.srv import GetParameters
    rclpy.init()
    node = rclpy.create_node('task01_readonly_recorded_state_replay')
    try:
        def call(kind, name, request):
            client = node.create_client(kind, name)
            if not client.wait_for_service(timeout_sec=3):
                raise RuntimeError(name + ' not ready')
            future = client.call_async(request)
            rclpy.spin_until_future_complete(node, future, timeout_sec=10)
            if not future.done():
                raise RuntimeError(name + ' timeout')
            response = future.result()
            node.destroy_client(client)
            return response

        req = GetPlanningScene.Request()
        req.components.components = (PlanningSceneComponents.WORLD_OBJECT_GEOMETRY |
                                     PlanningSceneComponents.ALLOWED_COLLISION_MATRIX)
        scene = call(GetPlanningScene, '/get_planning_scene', req).scene
        def pose(p):
            return {'position_m': [p.position.x, p.position.y, p.position.z],
                    'quaternion_xyzw': [p.orientation.x, p.orientation.y, p.orientation.z, p.orientation.w]}
        # MoveIt 会把 object.pose 与 primitive_poses 分开；不能把规范化的零局部位姿当作世界原点。
        objects = [{'id': o.id, 'frame': o.header.frame_id, 'object_pose': pose(o.pose),
                    'primitive_local_poses': [pose(v) for v in o.primitive_poses],
                    'sizes': [list(s.dimensions) for s in o.primitives]}
                   for o in scene.world.collision_objects]
        req = GetParameters.Request()
        req.names = ['robot_description']
        xml = call(GetParameters, '/move_group/get_parameters', req).values[0].string_value
        root = ET.fromstring(xml)
        collisions = {name: [ET.tostring(v, encoding='unicode') for v in
                      root.find('./link[@name="' + name + '"]').findall('collision')]
                      for name in ('left_fr3_link7', 'right_fr3_link7')}
        records = []
        links = ['left_fr3_link7', 'left_fr3_link8', 'right_fr3_link7', 'right_fr3_link8']
        for row in selected:
            out = {'physics_step': row['physics']['physics_step'], 'phase': row['phase_received_async'],
                   'cube': row['physics']['bodies'][0], 'suction_closed': row['suction_closed'],
                   'articulations': row['articulations'], 'replays': {},
                   'wrist_wall_contacts': [c for c in row['robot_collision_contacts']['pairs']
                                          if c['sensor_path'] == '/World/left_fr3/fr3_link7'
                                          and c['other_path'].endswith('/WallDeep')]}
            for field in ('positions_rad', 'position_targets_rad'):
                state = RobotState()
                state.is_diff = False
                for side, values in row['articulations'].items():
                    if side not in ('left', 'right') or values['dof_names'][:7] != [f'fr3_joint{i}' for i in range(1, 8)]:
                        raise ValueError('Unexpected robot/DOF mapping')
                    if not all(math.isfinite(v) for v in values[field][:7]):
                        raise ValueError('Nonfinite recorded arm joints')
                    state.joint_state.name.extend([side + '_' + n for n in values['dof_names'][:7]])
                    state.joint_state.position.extend(values[field][:7])
                req = GetPositionFK.Request()
                req.header.frame_id = 'world'
                req.fk_link_names = links
                req.robot_state = state
                response = call(GetPositionFK, '/compute_fk', req)
                if response.error_code.val != 1:
                    raise RuntimeError('FK error ' + str(response.error_code.val))
                fk = []
                for name, value in zip(response.fk_link_names, response.pose_stamped):
                    arm, link = name.split('_fr3_')
                    body = next(b for b in row['robots_physics']['bodies']
                                if b['prim_path'] == f'/World/{arm}_fr3/fr3_{link}')
                    physical = pose(value.pose)
                    physical['position_m'][0] += args.rail_shift_x
                    fk.append({'link': name, 'model_plus_rail_world_pose': physical,
                               'physics_pose': body, 'difference_norm_mm':
                               1000 * math.dist(physical['position_m'], body['position_m'])})
                req = GetStateValidity.Request()
                req.robot_state = state
                response = call(GetStateValidity, '/check_state_validity', req)
                out['replays'][field] = {'fk': fk, 'scene_valid': response.valid,
                    'contacts': [{'a': c.contact_body_1, 'b': c.contact_body_2, 'depth_m': c.depth,
                                  'position_m': [c.position.x, c.position.y, c.position.z]}
                                 for c in response.contacts]}
            records.append(out)
        print(json.dumps({'world_objects': objects, 'model_link7_collisions': collisions,
            'records': records, 'rail_shift_x_m': args.rail_shift_x,
            'boundary': 'Read-only exact joint replay. Remote scene includes current moving Cube; '
            'legitimate Cube/tool contact is not an insertion verdict. Rail shift is independently known, '
            'not fitted to FK. No physics/source or robot/scene command.'}, indent=2))
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
