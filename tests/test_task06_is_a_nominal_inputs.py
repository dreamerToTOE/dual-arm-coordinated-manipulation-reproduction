"""V2 源码映射/协议回归：纯离线，非物理或 IK 验收。"""
import copy
import json
from pathlib import Path
import unittest
import yaml

from platforms.offline_moveit.task06_is_a_scene_adapter.nominal_inputs import validate_world
from platforms.offline_moveit.task06_is_a_scene_adapter.source_audit import source_constants

ROOT = Path(__file__).resolve().parents[1]


class NominalInputsTests(unittest.TestCase):
    def setUp(self):
        self.scene = yaml.safe_load((ROOT/"configs/engineering/task06_is_a_task26_scene_v2.yaml").read_text())
        self.constants = {"BOX_INTERIOR_X": [.91, 1.16], "BOX_INTERIOR_Y": [-.314, .314],
            "BOX_WALL_THICKNESS": .02, "BOX_WALL_HEIGHT": .15, "TABLE_TOP_Z": .2,
            "TABLE_CENTER": [.55, 0., .1], "TABLE_SIZE": [1.5, .8, .2],
            "CUBE_SIZE": .12, "SLOT_B": [.35, 0., .26]}
        self.launch = 'p={"table_id":"task24_table","table_frame":"world","table_center":[.55,0,.1],"table_size":[1.2,.8,.2]}'
        self.cpp = '"task26_table" "task26_box_wall_deep" "task26_box_wall_minus_y" "task26_box_wall_plus_y" "task26_cube_" + std::to_string(index)'

    def test_all_source_boxes_and_ids(self):
        self.assertEqual(len(validate_world(self.scene, self.constants, self.launch, self.cpp)), 6)

    def test_missing_other_cube_rejected(self):
        self.scene["adapter_world_objects"].pop()
        with self.assertRaises(ValueError):
            validate_world(self.scene, self.constants, self.launch, self.cpp)

    def test_old_width_or_moved_box_rejected(self):
        for field in ("center_world_m", "size_m"):
            scene = copy.deepcopy(self.scene)
            scene["adapter_world_objects"][2][field][1] += .001
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_world(scene, self.constants, self.launch, self.cpp)

    def test_frame_identity_and_duplicate_rejected(self):
        for mutate in (lambda s: s["adapter_world_objects"][0].update(frame_id="base"),
                       lambda s: s["adapter_world_objects"][0].update(id="task26_cube_2")):
            scene = copy.deepcopy(self.scene); mutate(scene)
            with self.assertRaises(ValueError):
                validate_world(scene, self.constants, self.launch, self.cpp)

    def test_declared_targets_not_home_or_history(self):
        self.assertEqual(self.scene["nominal_endpoints"]["start"]["translation_m"], [.5, 0., .54])
        self.assertEqual(self.scene["nominal_endpoints"]["goal"]["translation_m"], [.79, .06, .28])
        for row in self.scene["nominal_endpoints"].values():
            self.assertEqual(row["quaternion_xyzw"], [0., 0., 0., 1.])

    def test_original_numeric_protocol_and_budget(self):
        p = json.loads((ROOT/"configs/engineering/task06_is_a_scene_adapter_v2.json").read_text())
        self.assertEqual(p["ik"]["max_candidate_pairs_per_endpoint"], 64)
        self.assertEqual(p["planner_seeds"], [7, 41, 20261012])
        self.assertEqual(p["ik"]["epsilon"], 1e-7)
        self.assertEqual(p["ik"]["joint_angle_policy"], "REJECT_RAW_OUT_OF_BOUNDS_NO_CLAMP_NO_PERIODIC_WRAP")
        l = json.loads((ROOT/p["local_protocol"]).read_text())
        self.assertEqual(l["position_tolerance_m"], 1e-8)
        self.assertEqual(l["rotation_tolerance_rad"], 1e-8)
        self.assertEqual(l["attached_cube_touch_links"], [])

    def test_no_execution_literal_interpretation(self):
        with self.assertRaises(ValueError):
            source_constants("A=__import__('os').system('false')", ["A"])


if __name__ == "__main__":
    unittest.main()
