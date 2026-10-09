"""离线软件回归：不导入 Isaac/ROS，不求 IK，不发送机器人命令。

从已修改的前代源码提取实际 FK 距离函数，以小型 RobotState 类型替身验证
Eigen 返回值生命周期与距离算术；这不是机器人运动学或物理资格证据。
"""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(os.environ.get(
    "TASK01_PREDECESSOR_ROOT",
    "/home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation",
))
SOURCE = ROOT / "ros_ws/src/fr3_dual_palletize/src/task26_truck_box_push_in.cpp"
BASE = "631b1f65656d025c1bb2173e874192f3fe4d355a"


class PredecessorReuseFixTest(unittest.TestCase):
    def test_owned_fk_return_and_distance_arithmetic(self):
        source = SOURCE.read_text()
        function = source.split("double cartesianLineDeviation(", 1)[1]
        function = "double cartesianLineDeviation(" + function.split(
            "\nbool planCommonCartesian(", 1)[0]
        self.assertIn("positions) -> Eigen::Vector3d", function)
        prelude = r'''
#include <Eigen/Geometry>
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <limits>
#include <memory>
#include <string>
#include <vector>
namespace moveit { namespace core {
using RobotModelConstPtr = std::shared_ptr<const int>;
struct RobotState {
  std::unique_ptr<Eigen::Isometry3d> transform;
  explicit RobotState(const RobotModelConstPtr&)
    : transform(std::make_unique<Eigen::Isometry3d>()) {}
  void setToDefaultValues() { transform->setIdentity(); }
  void setVariablePositions(const std::vector<std::string>&,
                            const std::vector<double>& positions) {
    transform->translation() = Eigen::Vector3d(positions[0], positions[1], positions[2]);
  }
  void update() {}
  const Eigen::Isometry3d& getGlobalLinkTransform(const std::string&) const {
    return *transform;
  }
};
}}
namespace trajectory_msgs { namespace msg {
struct Point { std::vector<double> positions; };
struct JointTrajectory {
  std::vector<std::string> joint_names;
  std::vector<Point> points;
};
}}
namespace geometry_msgs { namespace msg {
struct Pose { struct { double x, y, z; } position; };
}}
'''
        main = r'''
int main() {
  const auto model = std::make_shared<const int>(1);
  const geometry_msgs::msg::Pose goal{{0.1, 0.0, 0.0}};
  trajectory_msgs::msg::JointTrajectory trajectory{{"x", "y", "z"},
    {{{0.0, 0.0, 0.0}}, {{0.05, 0.0, 0.0}}, {{0.1, 0.0, 0.0}}}};
  for (int i = 0; i < 50; ++i) {
    assert(cartesianLineDeviation(model, "tcp", trajectory, goal) < 1e-12);
    trajectory.points[1].positions[1] = 0.008;
    assert(std::abs(cartesianLineDeviation(model, "tcp", trajectory, goal) - 0.008) < 1e-12);
    trajectory.points[1].positions[1] = 0.0;
  }
  trajectory.points.back().positions[0] = 0.11;
  assert(std::abs(cartesianLineDeviation(model, "tcp", trajectory, goal) - 0.01) < 1e-12);
  trajectory.points.clear();
  assert(std::isinf(cartesianLineDeviation(model, "tcp", trajectory, goal)));
  std::cout << "owned FK + exact/off-line/endpoint/empty arithmetic PASS\n";
}
'''
        with tempfile.TemporaryDirectory(prefix="task01_fk_unit_") as directory:
            executable = str(Path(directory) / "fk_unit")
            compiled = subprocess.run(
                ["g++", "-std=c++17", "-O1", "-g", "-fsanitize=address",
                 "-fno-omit-frame-pointer", "-fno-pie", "-no-pie",
                 "-I/usr/include/eigen3", "-x", "c++", "-", "-o", executable],
                input=prelude + function + main, text=True, capture_output=True, timeout=30,
            )
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            checked = subprocess.run([executable], text=True, capture_output=True, timeout=10)
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
            self.assertIn("PASS", checked.stdout)

    def test_existing_side_gate_shared_but_inner_predicate_preserved(self):
        source = SOURCE.read_text()
        macro_stack = []
        found = {}
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.startswith(("#if ", "#ifdef ", "#ifndef ")):
                macro_stack.append(stripped)
            elif stripped.startswith("#endif"):
                macro_stack.pop()
            if "if ((lift_already_done || planning_only)" in line:
                found["call"] = list(macro_stack)
                self.assertIn("!isStraightInsertTask(task) && side_preflight", line)
            if "side_preflight = [&]" in line:
                found["binding"] = list(macro_stack)
        self.assertEqual(set(found), {"call", "binding"})
        for stack in found.values():
            self.assertFalse(any("TASK27_FIVE_CUBE" in guard for guard in stack))
        self.assertLess(source.index("side_preflight = [&]"), source.index("if (!preplanPush("))
        self.assertIn("#ifdef TASK27_FIVE_CUBE\n          if (isInnerReferenceTask(task))", source)

    def test_runtime_patch_scope_and_thresholds(self):
        changed = subprocess.check_output(
            ["git", "diff", BASE, "--name-only"], cwd=ROOT, text=True,
        ).splitlines()
        self.assertEqual(changed, [str(SOURCE.relative_to(ROOT))])
        base_source = subprocess.check_output(
            ["git", "show", f"{BASE}:{SOURCE.relative_to(ROOT)}"], cwd=ROOT, text=True,
        )
        source = SOURCE.read_text()
        # 本轮没有修改任何原 constexpr 参数或8段背挡设定。
        constants = lambda text: [line for line in text.splitlines() if "constexpr" in line]
        self.assertEqual(constants(source), constants(base_source))


if __name__ == "__main__":
    unittest.main(verbosity=2)
