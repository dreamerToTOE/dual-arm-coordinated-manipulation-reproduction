"""[ENGINEERING] Original-op output algebra tests; USD in memory, no PhysX/GUI.

Requires the original bundled USD modules on the process-local import/library
paths. A normal Python without pxr skips these tests rather than starting Isaac.
These tests do not prove actor/q invariance; that requires the actual replay guard.
"""

from pathlib import Path
import runpy
import unittest

import numpy as np

try:
    from pxr import Gf, Usd, UsdGeom, UsdPhysics
except ImportError:
    Gf = Usd = UsdGeom = UsdPhysics = None


PROBE = Path(__file__).resolve().parents[1] / "platforms/isaac_ros2/probes/task01_single_cube_model_parity_gui.py"
HELPERS = runpy.run_path(str(PROBE), run_name="task01_body_pose_output_test_helpers")


@unittest.skipIf(Gf is None, "Use original bundled USD import/library paths; no SimulationApp fallback")
class OriginalBodyPoseOutputTests(unittest.TestCase):
    def setUp(self):
        self.stage = Usd.Stage.CreateInMemory()
        UsdGeom.Xform.Define(self.stage, "/World")
        self.roots, self.bodies, self.tools = {}, {}, {}
        for side, y in (("left", -.6), ("right", .6)):
            root = UsdGeom.Xform.Define(self.stage, "/World/" + side + "_fr3")
            root.AddTranslateOp().Set(Gf.Vec3d(.65, y, 0.))
            body = UsdGeom.Xform.Define(self.stage, str(root.GetPath()) + "/fr3_link7")
            body.AddTranslateOp().Set(Gf.Vec3d(.088, 0., 1.033))
            body.AddOrientOp(precision=UsdGeom.XformOp.PrecisionDouble).Set(Gf.Quatd(1.))
            body.AddScaleOp().Set(Gf.Vec3d(1.))
            UsdPhysics.RigidBodyAPI.Apply(body.GetPrim())
            tool = UsdGeom.Cube.Define(self.stage, str(body.GetPath()) + "/original_tool")
            tool.CreateSizeAttr(1.)
            tool.AddTranslateOp().Set(Gf.Vec3d(0., -.065 if side == "left" else .065, .08))
            tool.AddScaleOp().Set(Gf.Vec3f(.018, .13, .018))
            UsdPhysics.CollisionAPI.Apply(tool.GetPrim())
            self.roots[side], self.bodies[side], self.tools[side] = root, body, tool
        self.cube = UsdGeom.Cube.Define(self.stage, "/World/Cube")
        self.cube.CreateSizeAttr(1.)
        self.cube.AddTranslateOp(opSuffix="task26_pose").Set(Gf.Vec3d(.1, 0., .26))
        self.cube.AddScaleOp(opSuffix="task26_size").Set(Gf.Vec3f(.12))
        UsdPhysics.RigidBodyAPI.Apply(self.cube.GetPrim())
        UsdPhysics.CollisionAPI.Apply(self.cube.GetPrim())
        UsdPhysics.MassAPI.Apply(self.cube.GetPrim()).CreateMassAttr().Set(.8)
        joint = UsdPhysics.FixedJoint.Define(self.stage, "/World/left_fr3/original_joint")
        joint.CreateLocalPos0Attr().Set(Gf.Vec3f(0., 0., .107))

    def pose(self, position, axis=(0., 0., 1.), angle_deg=0.):
        matrix = Gf.Matrix4d(1.)
        matrix.SetRotate(Gf.Rotation(Gf.Vec3d(*axis), angle_deg))
        matrix.SetTranslateOnly(Gf.Vec3d(*position))
        return matrix

    def mirror(self, body_matrices):
        return HELPERS["mirror_existing_body_pose_ops"](self.stage, body_matrices, Gf, UsdGeom, np)

    def snapshot_attrs(self, prim):
        return {str(attr.GetName()): (str(attr.Get()), tuple(attr.GetTimeSamples()))
                for attr in prim.GetAttributes()}

    def fingerprint(self):
        enabled = [str(self.cube.GetPath())] + [str(tool.GetPath()) for tool in self.tools.values()]
        bodies = [str(self.cube.GetPath())] + [str(body.GetPath()) for body in self.bodies.values()]
        return HELPERS["original_geometry_fingerprint"](self.stage, enabled, bodies, UsdPhysics, UsdGeom)

    def assert_matrix_close(self, actual, expected):
        np.testing.assert_allclose(np.asarray(actual), np.asarray(expected), atol=1e-12, rtol=0.)

    def test_nonzero_both_base_translations_and_body_orientations(self):
        targets = {
            str(self.bodies["left"].GetPath()): self.pose((.55, -.216, .567), (1., 0., 0.), 170.),
            str(self.bodies["right"].GetPath()): self.pose((.55, .216, .567), (0., 1., 0.), -80.)}
        original_hash = self.fingerprint()
        changes = self.mirror(targets)
        self.assertEqual(len(changes), 2)
        self.assertEqual(self.fingerprint(), original_hash)
        for side, body in self.bodies.items():
            self.assert_matrix_close(body.ComputeLocalToWorldTransform(Usd.TimeCode.Default()), targets[str(body.GetPath())])
            self.assertEqual([str(op.GetOpName()) for op in body.GetOrderedXformOps()],
                             ["xformOp:translate", "xformOp:orient", "xformOp:scale"])

    def test_nonzero_parent_rotation_and_translation(self):
        root = self.roots["left"]
        root.AddOrientOp(precision=UsdGeom.XformOp.PrecisionDouble).Set(
            Gf.Rotation(Gf.Vec3d(0., 0., 1.), 33.).GetQuat())
        target = self.pose((.8, -.2, .6), (0., 1., 0.), 65.)
        self.mirror({str(self.bodies["left"].GetPath()): target})
        self.assert_matrix_close(self.bodies["left"].ComputeLocalToWorldTransform(Usd.TimeCode.Default()), target)

    def test_cube_original_point_twelve_scale_retained(self):
        target = self.pose((.55, 0., .38))
        before = self.snapshot_attrs(self.cube.GetPrim())
        original_hash = self.fingerprint()
        self.mirror({str(self.cube.GetPath()): target})
        after = self.snapshot_attrs(self.cube.GetPrim())
        self.assertEqual(before["xformOp:scale:task26_size"], after["xformOp:scale:task26_size"])
        self.assertEqual(before["xformOpOrder"], after["xformOpOrder"])
        self.assertEqual(self.fingerprint(), original_hash)
        expected = Gf.Matrix4d(1.)
        # The original scale attribute is float32, not an invented exact .12 value.
        original_scale = self.cube.GetPrim().GetAttribute("xformOp:scale:task26_size").Get()
        expected.SetScale(Gf.Vec3d(*map(float, original_scale)))
        expected = expected * target
        self.assert_matrix_close(self.cube.ComputeLocalToWorldTransform(Usd.TimeCode.Default()), expected)

    def test_tool_child_local_values_and_world_composition_retained(self):
        tool = self.tools["left"]
        before_attrs = self.snapshot_attrs(tool.GetPrim())
        original_local = tool.GetLocalTransformation()
        target = self.pose((.7, -.2, .4), (1., 0., 0.), 123.)
        self.mirror({str(self.bodies["left"].GetPath()): target})
        self.assertEqual(self.snapshot_attrs(tool.GetPrim()), before_attrs)
        self.assert_matrix_close(tool.GetLocalTransformation(), original_local)
        self.assert_matrix_close(tool.ComputeLocalToWorldTransform(Usd.TimeCode.Default()), original_local * target)

    def test_original_body_scale_change_is_detected_by_fingerprint(self):
        before = self.fingerprint()
        self.bodies["left"].GetPrim().GetAttribute("xformOp:scale").Set(Gf.Vec3f(2., 1., 1.))
        self.assertNotEqual(before, self.fingerprint())

    def test_original_shape_size_and_joint_attribute_changes_detected(self):
        before = self.fingerprint()
        self.tools["left"].GetSizeAttr().Set(2.)
        self.assertNotEqual(before, self.fingerprint())
        before = self.fingerprint()
        self.stage.GetPrimAtPath("/World/left_fr3/original_joint").GetAttribute("physics:localPos0").Set(Gf.Vec3f(0., 0., .2))
        self.assertNotEqual(before, self.fingerprint())

    def test_scaled_parent_rejected(self):
        self.roots["left"].AddScaleOp().Set(Gf.Vec3f(2., 1., 1.))
        with self.assertRaises(RuntimeError):
            self.mirror({str(self.bodies["left"].GetPath()): self.pose((.55, 0., .38))})

    def test_reordered_original_ops_rejected(self):
        body = self.bodies["left"]
        translate, orient, scale = body.GetOrderedXformOps()
        body.SetXformOpOrder([scale, translate, orient])
        with self.assertRaises(RuntimeError):
            self.mirror({str(body.GetPath()): self.pose((.55, 0., .38))})

    def test_duplicate_scale_ops_rejected(self):
        body = self.bodies["left"]
        body.AddScaleOp(opSuffix="extra").Set(Gf.Vec3f(2., 1., 1.))
        with self.assertRaises(RuntimeError):
            self.mirror({str(body.GetPath()): self.pose((.55, 0., .38))})

    def test_time_sampled_ops_rejected(self):
        body = self.bodies["left"]
        body.GetOrderedXformOps()[0].Set(Gf.Vec3d(.1, .2, .3), Usd.TimeCode(1.))
        with self.assertRaises(RuntimeError):
            self.mirror({str(body.GetPath()): self.pose((.55, 0., .38))})

    def test_unsupported_rotate_op_rejected(self):
        body = self.bodies["left"]
        body.AddRotateXOp().Set(20.)
        with self.assertRaises(RuntimeError):
            self.mirror({str(body.GetPath()): self.pose((.55, 0., .38))})

    def test_reset_xform_stack_rejected(self):
        body = self.bodies["left"]
        body.SetResetXformStack(True)
        with self.assertRaises(RuntimeError):
            self.mirror({str(body.GetPath()): self.pose((.55, 0., .38))})

    def test_absent_cube_orientation_op_not_added(self):
        before = self.snapshot_attrs(self.cube.GetPrim())
        with self.assertRaises(RuntimeError):
            self.mirror({str(self.cube.GetPath()): self.pose((.55, 0., .38), (0., 1., 0.), 20.)})
        self.assertEqual(self.snapshot_attrs(self.cube.GetPrim()), before)


if __name__ == "__main__":
    unittest.main()
