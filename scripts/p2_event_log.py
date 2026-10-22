#!/usr/bin/env python3
"""Event-preserving log policy for the P2 closed-loop runner (O2).

Every event keeps a complete, lossless summary: type, timestamps, sample ids,
innovations, iteration/convergence flags, domain-gate and stop reasons. Only the
large bulk payloads (contact matrices, singular values, full state copies,
solver diagnostics) are decimated to a fixed period, and are always written on
an exceptional event.

The ring buffer keeps the last N *complete* rows (all fields, numpy converted but
not decimated), so a failure dump is a replayable window rather than a summary.

Serialisation (O2 preflight fix): runner rows contain numpy arrays and scalars.
`_jsonable` converts them without changing finite values: ndarray -> nested
lists, np.floating -> python float, np.integer -> int, np.bool_ -> bool.
Non-finite values are NOT dropped and NOT clipped: they are written as the
strings "nan", "inf", "-inf", matching the legacy runner's `clean()` convention,
so a reader can still detect them.

Usage inside the runner:
    log = EventLog(gzip_handle, snapshot_period_s=1.0, ring_size=200)
    log.event(time_s, row)                 # normal heartbeat
    log.event(time_s, row, exceptional=True)
    log.dump_context(path)
"""
import json

import numpy as np

# Only genuinely bulky payloads are decimated. Per-sample vectors such as
# h_N_Nm / internal_N_Nm and the pose block `state` stay in every line because the
# half-step gate and the metric extraction read them at each logged tick.
BULK_KEYS = {
    "W", "D", "W_singular_values", "estimated_state", "solver",
    "old_applied_input_NA_body_m_s_rad_s",
}

# Keys that must exist in every written line (checked by the preflight test).
ALWAYS_PRESENT = {
    "phase", "time_s", "tick", "state", "h_N_Nm", "internal_N_Nm",
}


def _jsonable(value):
    """Convert numpy containers/scalars to JSON types without changing values."""
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if value != value:
            return "nan"
        if value == float("inf"):
            return "inf"
        if value == float("-inf"):
            return "-inf"
        return value
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


class EventLog:
    def __init__(self, handle, snapshot_period_s=1.0, ring_size=200):
        self.handle = handle
        self.period = float(snapshot_period_s)
        self.ring_size = int(ring_size)
        self.ring = []
        self.last_snapshot = None
        self.counters = {"events": 0, "snapshots": 0, "suppressed": 0}

    def _write(self, obj):
        data = json.dumps(obj, ensure_ascii=False,
                          allow_nan=False, separators=(",", ":")) + "\n"
        try:
            self.handle.write(data)
        except TypeError:                     # binary gzip handle
            self.handle.write(data.encode("utf-8"))

    def event(self, time_s, row, exceptional=False):
        full = _jsonable(dict(row))
        due = (self.last_snapshot is None or time_s - self.last_snapshot >= self.period
               or exceptional)
        if due:
            out = dict(full)
            self.last_snapshot = time_s
            self.counters["snapshots"] += 1
            out["bulk_snapshot"] = True
        else:
            out = {k: v for k, v in full.items() if k not in BULK_KEYS}
            self.counters["suppressed"] += 1
            out["bulk_snapshot"] = False
        self._write(out)
        self.counters["events"] += 1

        # ring keeps the complete row (bulk included) for replay
        self.ring.append(full)
        if len(self.ring) > self.ring_size:
            self.ring.pop(0)
        return out

    def dump_context(self, path, reason=None):
        """Write the full ring buffer; safe to call from finally/except."""
        payload = {"reason": reason, "counters": dict(self.counters),
                   "ring_size": self.ring_size,
                   "events": self.ring}
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False,
                                allow_nan=False, separators=(",", ":")) + "\n")

    def summary(self):
        return dict(self.counters)
