"""Pure source/mock tests only: never imports Isaac/ROS or starts a simulator."""
import ast
import math
from types import SimpleNamespace
import unittest

import reused_bridge as bridge


class PinnedReuseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.primitives, cls.namespace = bridge.load_primitives({
            "np": SimpleNamespace(asarray=lambda x, dtype=None: x, float64=float),
            "math": math,
        })

    def test_allowlist_excludes_full_application(self):
        methods = {k for k, v in self.primitives.__dict__.items() if callable(v)}
        methods.add("_stamp_key")  # staticmethod descriptor is not callable on Py3.10.
        self.assertEqual(methods, bridge.METHODS)
        for name in ("__init__", "_physics_step_inner", "_activate_batch", "_publish",
                     "_measured_joint_efforts", "_check_arrival"):
            self.assertNotIn(name, self.primitives.__dict__)

    def test_original_sg_and_rail_constants_preserved(self):
        ns = self.namespace
        self.assertEqual(ns["RIGID_GRASP_FORCE_LIMIT"], 1e6)
        self.assertEqual(ns["RIGID_GRASP_TORQUE_LIMIT"], 1e6)
        self.assertEqual(ns["GRASP_STIFFNESS"], {"left": 1e4, "right": 1e4})
        self.assertEqual(ns["GRASP_DAMPING"], {"left": 1e3, "right": 1e3})
        self.assertEqual(ns["RAIL_MAX_SPEED"], .20)
        self.assertEqual(ns["RAIL_HOLD_SEC"], .20)
        self.assertEqual(ns["RAIL_COMMAND_QUIET_SEC"], 1.0)

    def test_source_substitution_refused(self):
        with self.assertRaisesRegex(RuntimeError, "hash mismatch"):
            bridge.selected_source("print('not pinned')")

    def test_final_setter_failure_propagates(self):
        obj = self.primitives()
        obj.rail_base_y = {"left": -.6}
        obj.rail_carriage_z = 0.
        obj._author_translate = lambda *args: True
        def fail(*args, **kwargs):
            raise RuntimeError("mock setter failed")
        obj.articulations = {"left": SimpleNamespace(set_world_pose=fail)}
        with self.assertRaisesRegex(RuntimeError, "mock setter failed"):
            obj._write_rail_x("left", .75)

    def test_same_stamp_dual_atomic_submission(self):
        import threading
        obj = self.primitives()
        obj._lock = threading.Lock()
        obj._single_commands = {"left": None, "right": None}
        obj._dual_commands = {"left": ((1, 2), (), ()), "right": ((1, 2), (), ())}
        calls = []
        obj._apply_joint_command = lambda side, command: calls.append(side)
        obj._apply_pending_joint_commands()
        self.assertEqual(calls, ["left", "right"])
        self.assertEqual(obj._dual_commands, {"left": None, "right": None})

    def test_mismatched_stamp_never_paired(self):
        import threading
        obj = self.primitives()
        obj._lock = threading.Lock()
        obj._single_commands = {"left": None, "right": None}
        obj._dual_commands = {"left": ((1, 2), (), ()), "right": ((2, 2), (), ())}
        calls = []
        obj._apply_joint_command = lambda side, command: calls.append(side)
        obj._apply_pending_joint_commands()
        self.assertEqual(calls, [])
        self.assertIsNone(obj._dual_commands["left"])
        self.assertIsNotNone(obj._dual_commands["right"])

    def test_original_rail_check_calls_math_and_arrival_gate(self):
        obj = self.primitives()
        obj.rail_arrived = {"left": False}
        obj.rail_target = {"left": .750}
        obj.rail_measured = {"left": .650}
        obj.rail_stable = {"left": 0.0}
        position = [.650]
        writes = []
        obj._rail_read_x = lambda side: position[0]
        def write(side, x):
            writes.append(x)
            position[0] = x
        obj._write_rail_x = write
        obj._check_rail("left", 1/60)
        self.assertAlmostEqual(writes[-1], .650 + .20/60)
        self.assertFalse(obj.rail_arrived["left"])
        position[0] = .750
        for _ in range(13):
            obj._check_rail("left", 1/60)
        self.assertTrue(obj.rail_arrived["left"])
        self.assertAlmostEqual(obj.rail_measured["left"], .750)

    def test_original_sg_builder_parameters_and_mirrored_offsets(self):
        built = []
        class Gripper:
            def initialize(self, props):
                built.append(props)
                return True
        def transform():
            return SimpleNamespace(p=SimpleNamespace(), r=SimpleNamespace())
        primitives, _ = bridge.load_primitives({
            "omni": SimpleNamespace(physics=SimpleNamespace(tensors=SimpleNamespace(Transform=transform))),
            "Surface_Gripper": Gripper, "Surface_Gripper_Properties": SimpleNamespace,
        })
        obj = primitives()
        def prim(path):
            return SimpleNamespace(IsValid=lambda: path.endswith("/fr3_link8"))
        obj.stage = SimpleNamespace(GetPrimAtPath=prim)
        for side in ("left", "right"):
            obj._build_gripper(side)
        self.assertEqual([p.offset.p.y for p in built], [-.155, .155])
        for props in built:
            self.assertEqual(props.offset.p.z, .080)
            self.assertEqual(props.gripThreshold, .003)
            self.assertEqual(props.forceLimit, 1e6)
            self.assertEqual(props.torqueLimit, 1e6)
            self.assertEqual(props.bendAngle, 0.0)
            self.assertEqual(props.stiffness, 1e4)
            self.assertEqual(props.damping, 1e3)
            self.assertTrue(props.retryClose)
            self.assertFalse(props.disableGravity)


if __name__ == "__main__":
    unittest.main()
