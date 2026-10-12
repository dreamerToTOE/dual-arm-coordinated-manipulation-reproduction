"""合成输入门禁测试；不是原生规划/碰撞/物理验收。"""
import json
from pathlib import Path
import unittest

from platforms.offline_moveit.task06_is_a_scene_adapter.source_audit import (
    endpoint_gate, source_constants, xml_signature, JOINT_NAMES,
)


class AdapterTests(unittest.TestCase):
    def test_missing_both_endpoints(self):
        gate = endpoint_gate({"start": None, "goal": None})
        self.assertFalse(gate["ready"])
        self.assertEqual(gate["missing"], ["start", "goal"])

    def test_one_endpoint_does_not_make_pair(self):
        self.assertFalse(endpoint_gate({"start": {"q": [0]*14}, "goal": None})["ready"])

    def test_forged_complete_input_rejected(self):
        for source in ("HOME_OPEN", "SYNTHETIC", "SUPERSEDED_ARCHIVE", "VERIFIED"):
            with self.subTest(source=source), self.assertRaises(ValueError):
                endpoint_gate({"start": {"source": source}, "goal": {"source": source}})

    def test_literal_math_without_running_scene(self):
        self.assertEqual(source_constants("A=0.81+0.1\nB=(-A,A)\nC=1 if TASK27_MODE else 2", ["B", "C"]),
                         {"B": [-0.91, 0.91], "C": 2})

    def test_script_call_never_executed(self):
        with self.assertRaises(ValueError):
            source_constants("A=__import__('os').system('false')", ["A"])

    def test_xml_comments_and_layout_only(self):
        self.assertEqual(xml_signature('<robot a="1" b="2"> <link name="x"/> </robot>'),
                         xml_signature('<robot b="2" a="1"><!--note--><link name="x"/></robot>'))
        self.assertNotEqual(xml_signature('<box size="1 1 1"/>'), xml_signature('<box size="1 1 2"/>'))

    def test_joint_order(self):
        self.assertEqual(len(JOINT_NAMES), 14)
        self.assertEqual(JOINT_NAMES[0], "left_fr3_joint1")
        self.assertEqual(JOINT_NAMES[7], "right_fr3_joint1")
        self.assertEqual(JOINT_NAMES[-1], "right_fr3_joint7")

    def test_fixed_protocol_not_fake_endpoints(self):
        root = Path(__file__).resolve().parents[1]
        p = json.loads((root/"configs/engineering/task06_is_a_scene_adapter_v1.json").read_text())
        self.assertFalse(endpoint_gate(p["endpoints"])["ready"])
        self.assertFalse(p["runtime_allowed"])
        self.assertEqual(p["commands_allowed"], 0)


if __name__ == "__main__":
    unittest.main()
