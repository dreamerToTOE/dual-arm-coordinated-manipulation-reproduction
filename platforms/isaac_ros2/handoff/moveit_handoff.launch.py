"""[ENGINEERING] 原side-suction模型/MoveIt参数链，无旧Task24桌面发布器。

所有world对象由单Cube当前YAML构建。仅启动一个move_group，不运行旧Task27。
"""
import os
import hashlib
import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, LogInfo, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # 使用此前几何验收保存的同一个URDF/SRDF，避免install副本漂移。
    root = os.path.realpath(os.path.join(os.path.dirname(__file__), "../../.."))
    inputs = os.path.join(root, "results/20261006_TASK01_single_cube_geometry_probe01/raw")
    with open(os.path.join(inputs, "robot.urdf"), encoding="utf-8") as stream:
        urdf = stream.read()
    with open(os.path.join(inputs, "robot.srdf"), encoding="utf-8") as stream:
        srdf = stream.read()
    if hashlib.sha256(urdf.encode()).hexdigest() != "a9d6a364c89b9e72e51da962d16ee44de45595429339b51004a59211b312939b" or \
       hashlib.sha256(srdf.encode()).hexdigest() != "11b89277bfa5fb7bcedfa35f8285507e88d2c793df6ba8e04daf12c8eb8d023a":
        raise RuntimeError("Recorded URDF/SRDF changed; no silent model substitution")
    package_path = get_package_share_directory("franka_fr3_moveit_config")
    with open(os.path.join(package_path, "config/ompl_planning.yaml"), encoding="utf-8") as stream:
        ompl = yaml.safe_load(stream)
    for group in ("left_arm", "right_arm", "dual_arm"):
        ompl[group] = {"planner_configs": ["RRTConnectkConfigDefault"]}
    # 固定已验证LMA数值设置，独立FK/碰撞验收门限不由此放宽。
    kinematics = {"robot_description_kinematics": {
        group: {"kinematics_solver": "lma_kinematics_plugin/LMAKinematicsPlugin",
                "kinematics_solver_search_resolution": .005,
                "kinematics_solver_timeout": .010,
                "epsilon": 1e-7, "orientation_vs_position": .01}
        for group in ("left_arm", "right_arm")}}
    pipeline = {"planning_plugin": "ompl_interface/OMPLPlanner",
                "request_adapters": (
                    "default_planner_request_adapters/AddTimeOptimalParameterization "
                    "default_planner_request_adapters/ResolveConstraintFrames "
                    "default_planner_request_adapters/FixWorkspaceBounds "
                    "default_planner_request_adapters/FixStartStateBounds "
                    "default_planner_request_adapters/FixStartStateCollision "
                    "default_planner_request_adapters/FixStartStatePathConstraints"),
                "start_state_max_bounds_error": .1}
    pipeline.update(ompl)
    descriptions = {"robot_description": urdf, "robot_description_semantic": srdf}
    # 与已经通过A136探针相同的两种参数lookup前缀，数值不改。
    flat_kinematics = {
        group: dict(values) for group, values in
        kinematics["robot_description_kinematics"].items()}
    common = [descriptions, kinematics, flat_kinematics, {"use_sim_time": True}]
    driver = Node(executable=LaunchConfiguration("driver"), name="task01_rear_handoff",
                  output="screen", parameters=common + [{
                      "benchmark_config": LaunchConfiguration("benchmark_config"),
                      "snapshot_topic": "/task01/ready_snapshot", "deadline_sec": 120.0,
                      "joint_settle_limit_rad": .01, "cube_drift_guard_m": .005}])

    def driver_finished(event, context):
        # driver结束后释放本launch拥有的MoveIt节点；exit0不能替代完整capture证据。
        del context
        return [LogInfo(msg=f"TASK01 handoff driver exited: returncode={event.returncode}; stopping owned MoveIt nodes."),
                EmitEvent(event=Shutdown(reason="Bounded TASK01 handoff driver finished"))]

    return LaunchDescription([
        DeclareLaunchArgument("driver", default_value=os.path.join(root, "build/task01_handoff/task01_rear_handoff")),
        DeclareLaunchArgument("benchmark_config", default_value=os.path.join(root, "configs/benchmark/benchmark_v1.yaml")),
        Node(package="moveit_ros_move_group", executable="move_group", name="move_group",
             output="screen", parameters=common + [{"move_group": pipeline,
                 "publish_planning_scene": True, "publish_geometry_updates": True,
                 "publish_state_updates": True, "publish_transforms_updates": True}]),
        Node(package="robot_state_publisher", executable="robot_state_publisher",
             name="task01_robot_state_publisher", output="screen", parameters=common),
        RegisterEventHandler(OnProcessExit(target_action=driver, on_exit=driver_finished)),
        driver,
    ])
