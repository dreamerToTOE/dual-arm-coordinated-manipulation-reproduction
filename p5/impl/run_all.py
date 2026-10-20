"""P5 implementation runner: one command, one ledger.

    PYTHONPATH=. /usr/bin/python3.10 run_all.py                 # everything
    PYTHONPATH=. /usr/bin/python3.10 run_all.py --gate G1       # only G1 tasks
    PYTHONPATH=. /usr/bin/python3.10 run_all.py --only T04      # one task
    PYTHONPATH=. /usr/bin/python3.10 run_all.py --list          # show registry

Outputs
-------
p5/evidence/P5_impl_checks.json      machine-readable ledger (per check + per gate)
p5/evidence/impl_checks/<TID>.json   per-task ledger, written as soon as the task ends
p5/evidence/P5_impl_checks.md        paste-ready summary table for plan section 6

Gate logic (plan section 3.2)
-----------------------------
G1 needs T01 T02 T04 T06; G2 needs T03 T05 T07 *and* G1; G3 needs T08 *and* G2;
G4 needs T10 *and* G3.  A task is only executed when the gate it belongs to has
all of its upstream gates green -- otherwise it is recorded as SKIPPED_BY_GATE so
that a downstream number can never be read as if it had been produced in a sound
pipeline.  T10 additionally obeys N10.3: if any of T01-T08 is not PASS, T10 is
recorded as BLOCKED_BY_UPSTREAM and is not even attempted.

Nothing here decides whether a check is meaningful; that lives in the task
modules.  This file only orchestrates, timestamps, and aggregates.
"""

import argparse
import importlib
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
EVIDENCE = os.path.join(REPO, "p5", "evidence")
FIGDIR = os.path.join(EVIDENCE, "figures", "impl")

if HERE not in sys.path:
    sys.path.insert(0, HERE)

from p5core.results import Recorder  # noqa: E402

# (task id, module, gate, one-line role)
TASKS = [
    ("T01", "tasks.t01_tau", "G1", "synchronisation allocation tau, Eq.(8)"),
    ("T02", "tasks.t02_lpv", "G1", "LPV scheduler + common Lyapunov matrix"),
    ("T04", "tasks.t04_qp_core", "G1", "centralised QP IK, Eq.(17)-(18)"),
    ("T06", "tasks.t06_sca_2d", "G1", "2D SCA boundary, Eq.(24)-(25)"),
    ("T03", "tasks.t03_virtual_object", "G2", "virtual-object DS, Eq.(9)-(11)-(36)"),
    ("T05", "tasks.t05_lvi", "G2", "LVI projection solver, Eq.(19)-(23)"),
    ("T07", "tasks.t07_sca_36d", "G2", "36D model, chain rule, calibration"),
    ("T08", "tasks.t08_sca_closed_loop", "G3", "SCA inside the QP, Eq.(26)-(27)"),
    ("T10", "tasks.t10_e2e", "G4", "end-to-end mechanism chain"),
]

#: T09 is deliberately absent: the review did not authorise it this cycle.
NOT_RUN = {"T09": "NOT_AUTHORIZED_THIS_CYCLE"}

GATES = [
    ("G1", ["T01", "T02", "T04", "T06"], []),
    ("G2", ["T03", "T05", "T07"], ["G1"]),
    ("G3", ["T08"], ["G2"]),
    ("G4", ["T10"], ["G3"]),
]

GATE_ORDER = [g[0] for g in GATES]


def _load(tid, modname):
    """Import a task module; return (module, None) or (None, error text)."""
    try:
        return importlib.import_module(modname), None
    except ModuleNotFoundError as exc:
        if exc.name and exc.name.split(".")[0] == "tasks":
            return None, "NOT_IMPLEMENTED: %s" % exc
        return None, "IMPORT_ERROR: %s" % exc
    except Exception:
        return None, "IMPORT_ERROR:\n" + traceback.format_exc()


def run_task(tid, modname, role):
    os.makedirs(FIGDIR, exist_ok=True)
    rec = Recorder(tid, FIGDIR, metadata={"role": role, "module": modname})

    mod, err = _load(tid, modname)
    if mod is None:
        rec.checks.append({"id": tid + ".module", "kind": "positive", "ok": False,
                           "detail": err, "info": {}})
        rec.metric("load_error", (err or "")[:2000])
        out = rec.to_dict()
        out["status"] = "NOT_IMPLEMENTED" if str(err).startswith("NOT_IMPLEMENTED") else "ERROR"
        return out

    try:
        mod.run(rec)
    except Exception:
        tb = traceback.format_exc()
        rec.checks.append({"id": tid + ".run", "kind": "positive", "ok": False,
                           "detail": "exception during run():\n" + tb[-3000:], "info": {}})
        out = rec.to_dict()
        out["status"] = "ERROR"
        out["traceback"] = tb[-4000:]
        return out

    return rec.to_dict()


def evaluate_gates(results):
    """Return {gate: {...}} with status PASS/FAIL/BLOCKED/NOT_RUN."""
    gate_state = {}
    for gate, members, upstream in GATES:
        missing = []
        for need in upstream:
            if gate_state.get(need, {}).get("status") != "PASS":
                missing.append(need)
        if missing:
            gate_state[gate] = {
                "status": "BLOCKED_BY_UPSTREAM",
                "blocked_by": missing,
                "members": members,
                "detail": "upstream gate(s) not PASS: " + ", ".join(missing),
            }
            continue

        states = {m: results.get(m, {}).get("status", "NOT_RUN") for m in members}
        not_pass = [m for m, s in states.items() if s != "PASS"]
        gate_state[gate] = {
            "status": "PASS" if not not_pass else "FAIL",
            "blocked_by": [],
            "members": members,
            "member_status": states,
            "detail": ("all members PASS" if not not_pass
                       else "not PASS: " + ", ".join("%s=%s" % (m, states[m]) for m in not_pass)),
        }
    return gate_state


def _fmt_row(cells, widths):
    return "| " + " | ".join(str(c).ljust(w) for c, w in zip(cells, widths)) + " |"


def write_markdown(payload, path):
    rows = [("task", "gate", "status", "checks", "pos", "neg", "failed", "wall [s]")]
    for tid, _m, gate, _role in TASKS:
        r = payload["tasks"].get(tid)
        if r is None:
            rows.append((tid, gate, "NOT_RUN", "-", "-", "-", "-", "-"))
            continue
        rows.append((tid, gate, r["status"], r.get("n_checks", "-"),
                     r.get("n_positive", "-"), r.get("n_negative", "-"),
                     r.get("n_failed", "-"), r.get("wall_time_s", "-")))
    for tid, why in NOT_RUN.items():
        rows.append((tid, "-", why, "-", "-", "-", "-", "-"))
    widths = [max(len(str(r[i])) for r in rows) for i in range(len(rows[0]))]
    lines = ["# P5 implementation check ledger", "",
             "Generated by `p5/impl/run_all.py`. Counts are ACTUAL, never estimated.", "",
             _fmt_row(*rows[0:1], widths), "|" + "|".join("-" * (w + 2) for w in widths) + "|"]
    for row in rows[1:]:
        lines.append(_fmt_row(row, widths))
    lines += ["", "## Gates", ""]
    for gate in GATE_ORDER:
        g = payload["gates"][gate]
        lines.append("- **%s**: %s -- %s" % (gate, g["status"], g["detail"]))
    if payload.get("totals"):
        t = payload["totals"]
        lines += ["", "## Totals", "",
                  "%d checks (%d positive, %d negative), %d failed, wall %.1f s"
                  % (t["n_checks"], t["n_positive"], t["n_negative"], t["n_failed"], t["wall_s"])]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description="run the P5 implementation checks")
    ap.add_argument("--only", default=None,
                    help="comma separated task ids, e.g. T04 or T01,T02 (bypasses gate gating)")
    ap.add_argument("--gate", default=None, choices=GATE_ORDER, help="run one gate only")
    ap.add_argument("--list", action="store_true", help="print the registry and exit")
    ap.add_argument("--out", default=os.path.join(EVIDENCE, "P5_impl_checks.json"))
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    if args.list:
        for tid, mod, gate, role in TASKS:
            print("%s  %-4s %-26s %s" % (tid, gate, mod, role))
        for tid, why in NOT_RUN.items():
            print("%s  ---- %-26s %s" % (tid, "-", why))
        return 0

    wanted = None
    if args.only:
        wanted = [t.strip().upper() for t in args.only.split(",") if t.strip()]
    elif args.gate:
        wanted = [m for g, members, _u in GATES if g == args.gate for m in members]

    results = {}
    order = [t for t in TASKS if wanted is None or t[0] in wanted]

    # Gate state is recomputed after every task so that downstream members can be
    # skipped the moment an upstream gate fails.
    for tid, modname, gate, role in order:
        upstream_ok = True
        if wanted is None:
            state = evaluate_gates(results)
            for gate_name, members, upstream in GATES:
                if tid in members and upstream:
                    if any(state.get(u, {}).get("status") != "PASS" for u in upstream):
                        upstream_ok = False
        if tid == "T10" and wanted is None:
            upstream = ["T%02d" % i for i in (1, 2, 3, 4, 5, 6, 7, 8)]
            bad = [t for t in upstream if results.get(t, {}).get("status") != "PASS"]
            if bad:
                results[tid] = {"task": tid, "status": "BLOCKED_BY_UPSTREAM",
                                "n_checks": 0, "n_positive": 0, "n_negative": 0,
                                "n_failed": 0, "blocked_by": bad,
                                "detail": "N10.3: " + ", ".join(bad) + " not PASS"}
                if not args.quiet:
                    print("%s  BLOCKED_BY_UPSTREAM (%s)" % (tid, ", ".join(bad)))
                continue
        if not upstream_ok:
            results[tid] = {"task": tid, "status": "SKIPPED_BY_GATE",
                            "n_checks": 0, "n_positive": 0, "n_negative": 0,
                            "n_failed": 0, "detail": "gate %s not green" % gate}
            if not args.quiet:
                print("%s  SKIPPED_BY_GATE" % tid)
            continue

        out = run_task(tid, modname, role)
        results[tid] = out
        os.makedirs(os.path.join(EVIDENCE, "impl_checks"), exist_ok=True)
        with open(os.path.join(EVIDENCE, "impl_checks", tid + ".json"), "w",
                  encoding="utf-8") as fh:
            json.dump(out, fh, indent=2, ensure_ascii=False)
        if not args.quiet:
            print("%s  %-19s checks=%3d (pos %3d / neg %3d) failed=%d  %5.1fs"
                  % (tid, out["status"], out.get("n_checks", 0), out.get("n_positive", 0),
                     out.get("n_negative", 0), out.get("n_failed", 0),
                     out.get("wall_time_s", 0.0)))
            for c in out.get("checks", []):
                if not c["ok"]:
                    print("      FAIL %-8s %s" % (c["id"], (c.get("detail") or "")[:200]))

    gates = evaluate_gates(results)
    totals = {
        "n_checks": sum(r.get("n_checks", 0) for r in results.values()),
        "n_positive": sum(r.get("n_positive", 0) for r in results.values()),
        "n_negative": sum(r.get("n_negative", 0) for r in results.values()),
        "n_failed": sum(r.get("n_failed", 0) for r in results.values()),
        "wall_s": round(sum(r.get("wall_time_s", 0.0) for r in results.values()), 3),
    }
    payload = {
        "paper": "Mirrazavi Salehian, Figueroa, Billard, IJRR 37(6):583-603, 2018",
        "doi": "10.1177/0278364918765952",
        "branch": os.popen("git -C %s rev-parse --abbrev-ref HEAD" % REPO).read().strip(),
        "commit": os.popen("git -C %s rev-parse HEAD" % REPO).read().strip(),
        "runner": "p5/impl/run_all.py",
        "tasks": results,
        "not_run": NOT_RUN,
        "gates": gates,
        "totals": totals,
    }
    os.makedirs(EVIDENCE, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    write_markdown(payload, os.path.join(EVIDENCE, "P5_impl_checks.md"))

    if not args.quiet:
        print("-" * 62)
        for gate in GATE_ORDER:
            print("%-3s %-20s %s" % (gate, gates[gate]["status"], gates[gate]["detail"]))
        print("total: %d checks (%d pos / %d neg), %d failed, %.1fs"
              % (totals["n_checks"], totals["n_positive"], totals["n_negative"],
                 totals["n_failed"], totals["wall_s"]))
        print("ledger: %s" % args.out)

    any_fail = totals["n_failed"] > 0 or any(
        g["status"] == "FAIL" for g in gates.values())
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
