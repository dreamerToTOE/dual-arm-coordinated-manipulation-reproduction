"""Check/metric recorder shared by every P5 task.

Design rules that come straight from the review:

* A *positive* check passes when the implementation behaves as the paper says.
* A *negative* check passes when a deliberately defective implementation is
  **detected**.  Recording a negative control as "expected failure observed"
  is what stops the suite from being decorative.
* Nothing is pre-counted: the totals in the final ledger are whatever this
  recorder actually saw.
"""

import json
import os
import platform
import time


class Recorder:
    def __init__(self, task, figures_dir, metadata=None):
        self.task = task
        self.figures_dir = figures_dir
        self.checks = []
        self.metrics = {}
        self.figures = []
        self.metadata = dict(metadata or {})
        self.t0 = time.time()

    # ---------------------------------------------------------------- checks
    def check(self, cid, ok, detail="", **info):
        self.checks.append({"id": cid, "kind": "positive", "ok": bool(ok),
                            "detail": detail, "info": _plain(info)})
        return bool(ok)

    def defect(self, cid, detected, detail="", **info):
        """Negative control: pass when the injected defect *was* detected."""
        self.checks.append({"id": cid, "kind": "negative", "ok": bool(detected),
                            "detail": detail, "info": _plain(info)})
        return bool(detected)

    def le(self, cid, value, tol, detail="", **info):
        info = dict(info)
        info.setdefault("value", float(value))
        info.setdefault("tol", float(tol))
        return self.check(cid, value <= tol, detail or "%s <= %s" % (value, tol), **info)

    def ge(self, cid, value, floor, detail="", **info):
        info = dict(info)
        info.setdefault("value", float(value))
        info.setdefault("floor", float(floor))
        return self.check(cid, value >= floor, detail or "%s >= %s" % (value, floor), **info)

    # --------------------------------------------------------------- metrics
    def metric(self, name, value):
        self.metrics[name] = _plain(value)

    # --------------------------------------------------------------- figures
    def figure(self, name, path):
        self.figures.append({"name": name, "path": path})

    # ----------------------------------------------------------------- state
    @property
    def n_checks(self):
        return len(self.checks)

    @property
    def n_failed(self):
        return sum(1 for c in self.checks if not c["ok"])

    @property
    def status(self):
        return "PASS" if self.n_failed == 0 else "FAIL"

    def to_dict(self):
        return {
            "task": self.task,
            "status": self.status,
            "n_checks": self.n_checks,
            "n_positive": sum(1 for c in self.checks if c["kind"] == "positive"),
            "n_negative": sum(1 for c in self.checks if c["kind"] == "negative"),
            "n_failed": self.n_failed,
            "checks": self.checks,
            "metrics": self.metrics,
            "figures": self.figures,
            "metadata": self.metadata,
            "wall_time_s": round(time.time() - self.t0, 3),
            "python": platform.python_version(),
        }

    def dump(self, path):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=2, ensure_ascii=False)
        return path


def _plain(obj):
    """Make numpy scalars/arrays JSON-safe without importing numpy at module load."""
    if isinstance(obj, dict):
        return {str(k): _plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_plain(v) for v in obj]
    if hasattr(obj, "tolist"):
        return obj.tolist()
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)


def require(cond, msg):
    """Hard failure used for preconditions that make a whole task meaningless."""
    if not cond:
        raise RuntimeError(msg)
