#!/usr/bin/env python3
"""Event-preserving log policy for the P2 closed-loop runner (O2).

Every event keeps a complete, lossless summary: type, timestamps, sample ids,
innovations, iteration/convergence flags, domain-gate and stop reasons. Only the
large bulk payloads (matrices, full state copies, solver diagnostics) are
decimated to a fixed period, and are always written on an exceptional event.

A bounded ring buffer keeps the last N events so that the pre-failure context can
be dumped even if the process is aborted from an exception handler.

Usage inside the runner:
    log = EventLog(gzip_handle, snapshot_period_s=1.0, ring_size=200)
    log.event(time_s, row)                 # normal heartbeat
    log.event(time_s, row, exceptional=True)
    log.dump_context(path)
"""
import json

# Only genuinely bulky payloads are decimated. Per-sample vectors such as
# h_N_Nm / internal_N_Nm stay in every line because the half-step gate and the
# metric extraction read them at each logged tick.
BULK_KEYS = {
    "W", "D", "W_singular_values", "estimated_state", "solver",
    "old_applied_input_NA_body_m_s_rad_s",
}

# Fields that must never be dropped, even if they were added to BULK_KEYS later.
REQUIRED_KEYS = {
    "phase", "time_s", "global_case_time_s", "tick",
    "converged", "iterations", "consecutive_nonconverged",
    "observations_consumed", "prediction_interval_s",
    "innovation_before", "innovation_after", "stop_requested",
    "reason", "type", "P_diagonal",
}


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
        row = dict(row)
        due = (self.last_snapshot is None or time_s - self.last_snapshot >= self.period
               or exceptional)
        if due:
            out = row
            self.last_snapshot = time_s
            self.counters["snapshots"] += 1
            out["bulk_snapshot"] = True
        else:
            out = {k: v for k, v in row.items() if k not in BULK_KEYS}
            self.counters["suppressed"] += 1
            out["bulk_snapshot"] = False
        self._write(out)
        self.counters["events"] += 1

        record = {k: out[k] for k in REQUIRED_KEYS if k in out}
        record["_bulk_snapshot"] = out["bulk_snapshot"]
        self.ring.append(record)
        if len(self.ring) > self.ring_size:
            self.ring.pop(0)
        return out

    def dump_context(self, path, reason=None):
        """Write the ring buffer; safe to call from finally/except."""
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"reason": reason, "counters": self.counters,
                                 "events": self.ring}, ensure_ascii=False) + "\n")

    def summary(self):
        return dict(self.counters)
