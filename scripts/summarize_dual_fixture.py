"""[ENGINEERING] 新协议证据解析；旧五件PASS不能充当双吸附协议PASS。"""
import argparse
import json
from pathlib import Path
import re


FIXTURES = ("task27_plus_outer", "task27_minus_outer", "task27_plus_inner")


def protocol_evidence(text):
    result = {}
    for name in FIXTURES:
        start = text.find(name + " DUAL_REAR_PRIMARY_X: ")
        swap = text.find(name + " DUAL_ROLE_SWAP: ", start) if start >= 0 else -1
        release = text.find("object=" + name + " phase=RELEASE_REQUEST", swap) if swap >= 0 else -1
        window = text[start:release] if start >= 0 and release > start else ""
        stages = {}
        for stage in ("DUAL_REAR_PRIMARY_X", "DUAL_SIDE_PRIMARY_Y"):
            samples = re.findall(re.escape(name + " " + stage) +
                r" slice (\d+) rear=(CLOSED|OPEN) side=(CLOSED|OPEN)", window)
            stages[stage] = {
                "slices": [int(index) for index, _, _ in samples],
                "all_both_closed": bool(samples) and all(
                    rear == side == "CLOSED" for _, rear, side in samples),
            }
        valid = (start >= 0 and start < swap < release and all(
            stage["slices"] == list(range(1, 17)) and stage["all_both_closed"]
            for stage in stages.values()))
        result[name] = {"role_swap_before_release": start >= 0 and start < swap < release,
                        "stages": stages, "dual_protocol_logged": valid}
    completed = [int(index) for index in re.findall(r"Task27 batch (\d+) PASS:", text)]
    return {"fixtures": result, "completed_batches": completed,
            "full_new_protocol_logged": completed == [1, 2, 3, 4, 5] and all(
                record["dual_protocol_logged"] for record in result.values()),
            "boundary": "Controller/Bridge state evidence only; physical success also needs exit code and independent actual poses. Not contact-force, timing-synchronized wrench, GUI acceptance, reliability or benchmark freeze."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    args = parser.parse_args()
    print(json.dumps(protocol_evidence(args.log.read_text(encoding="utf-8")), indent=2))


if __name__ == "__main__":
    main()
