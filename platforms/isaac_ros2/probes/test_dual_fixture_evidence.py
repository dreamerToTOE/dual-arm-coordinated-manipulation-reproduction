"""[ENGINEERING] 防止把旧协议的5/5或未释放的中间状态误算新协议通过。"""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from summarize_dual_fixture import FIXTURES, protocol_evidence


def fixture_log(name):
    rows = [name + " DUAL_REAR_PRIMARY_X: rear=right side=left; both suction CLOSED."]
    for stage in ("DUAL_REAR_PRIMARY_X", "DUAL_SIDE_PRIMARY_Y"):
        if stage.endswith("Y"):
            rows.append(name + " DUAL_ROLE_SWAP: side PRIMARY, rear deep-wall HOLD; no suction release.")
        rows.extend(name + f" {stage} slice {index} rear=CLOSED side=CLOSED" for index in range(1, 17))
    rows.append("TASK01_RELEASE_PHASE object=" + name + " phase=RELEASE_REQUEST.")
    return "\n".join(rows)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.batch_lines = "\n".join(f"Task27 batch {i} PASS:" for i in range(1, 6))
        self.complete = "\n".join(fixture_log(name) for name in FIXTURES) + "\n" + self.batch_lines

    def test_complete_protocol(self):
        self.assertTrue(protocol_evidence(self.complete)["full_new_protocol_logged"])

    def test_old_five_pass_is_not_new(self):
        self.assertFalse(protocol_evidence(self.batch_lines)["full_new_protocol_logged"])

    def test_open_helper_rejected(self):
        self.assertFalse(protocol_evidence(self.complete.replace("side=CLOSED", "side=OPEN", 1))["full_new_protocol_logged"])

    def test_role_swap_required(self):
        self.assertFalse(protocol_evidence(self.complete.replace("DUAL_ROLE_SWAP:", "MISSING_SWAP:", 1))["full_new_protocol_logged"])

    def test_unreleased_is_not_completed(self):
        self.assertFalse(protocol_evidence(self.complete.replace("phase=RELEASE_REQUEST", "phase=UNRELEASED", 1))["full_new_protocol_logged"])

    def test_missing_slice_rejected(self):
        self.assertFalse(protocol_evidence(self.complete.replace("slice 16 rear=", "slice 17 rear=", 1))["full_new_protocol_logged"])

    def test_failed_partial_retains_x_evidence(self):
        rows = fixture_log(FIXTURES[0]).split("DUAL_ROLE_SWAP:")[0]
        evidence = protocol_evidence(rows)
        self.assertFalse(evidence["full_new_protocol_logged"])
        self.assertEqual(evidence["fixtures"][FIXTURES[0]]["stages"]["DUAL_REAR_PRIMARY_X"]["slices"], list(range(1, 17)))


if __name__ == "__main__":
    unittest.main()
