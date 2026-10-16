"""Saved-byte inventory only. Does not import or invoke any experiment runner."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
RUN = "20261015_R2_ABB_CBIRRT_D_TAIL02"
OUTPUT = ROOT / "reports/P4_FULL_R2_ABB_CBIRRT_D_TAIL02_EVIDENCE_INVENTORY_20261016.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    prefix = ROOT / "results/p4_full" / RUN
    execution = prefix / "execution.json"
    charge = Path(str(prefix) + ".supervision.charge.json")
    if not execution.is_file() and not charge.is_file():
        raise RuntimeError("NO_SAVED_EXECUTION_OR_SUPERVISION_CHARGE; INVENTORY_NOT_CREATED")
    e = json.loads(execution.read_text()) if execution.is_file() else None
    c = json.loads(charge.read_text()) if charge.is_file() else None
    paths = []
    if prefix.is_dir():
        paths.extend(p for p in prefix.rglob("*") if p.is_file())
    paths.extend(p for p in prefix.parent.glob(RUN + ".supervision.*") if p.is_file())
    if e is not None:
        paths.extend(ROOT / e[k] for k in ("claim", "protocol"))
    inventory = [
        {"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size, "sha256": digest(p)}
        for p in sorted(set(paths))
    ]
    summary = {
        "execution_present": e is not None,
        "charge_present": c is not None,
        "status": None if e is None else e.get("status"),
        "classification": None if e is None else e.get("classification"),
        "completed_new_dispatch_ids": None if e is None else e.get("completed_new_dispatch_ids"),
        "UNKNOWN_new_dispatch_ids": None if e is None else e.get("UNKNOWN_new_dispatch_ids"),
        "counts": None if e is None else e.get("counts"),
        "source_process_registry": None if e is None else e.get("source_process_registry"),
        "internal_wall_s": None if e is None else e.get("wall_s"),
        "internal_cpu_s": None if e is None else e.get("cpu_s"),
        "external_charge_wall_s": None if c is None else c.get("wall_s"),
        "external_charge_cpu_s": None if c is None else c.get("cpu_s"),
        "external_time_fields": None if c is None else c.get("time_fields"),
        "external_timing_valid": None if c is None else c.get("timing_valid"),
        "external_caps_pass": None if c is None else c.get("wall_CPU_caps_pass"),
        "external_process_exit0": None if c is None else c.get("completed_process_exit0"),
        "termination_reason": None if e is None else e.get("termination_reason"),
        "diagnostics": None if e is None else e.get("diagnostics"),
    }
    report = {
        "schema": "P4_R2_ABB_CBIRRT_D_TAIL02_SAVED_BYTE_INVENTORY_V1",
        "qualification_audit": False,
        "scientific_calls": 0,
        "runner_imports": 0,
        "source_files_modified": 0,
        "experimental_files_modified": 0,
        "independent_POST_still_required": True,
        "summary": summary,
        "files": inventory,
    }
    with OUTPUT.open("x") as stream:
        json.dump(report, stream, ensure_ascii=False, allow_nan=False, indent=2)
        stream.write("\n")
    print(json.dumps({"inventory": str(OUTPUT.relative_to(ROOT)), "sha256": digest(OUTPUT), "files": len(inventory), "summary": summary}, ensure_ascii=False))


if __name__ == "__main__":
    main()
