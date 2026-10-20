"""P3 assembly-stage command composition — paper Eq.(23)-(26).

[ORIGINAL] compositions:
    w_approach = w_push                       (23)
    w_search   = w_push + w_spiral            (24)
    w_align    = w_push + w_wiggle + w_rub    (25)
    w_insert   = w_push                       (26)

[ADAPTATION] Stage *boundaries*. The paper switches stages manually
(p.8572: "transitions between the stages were manually controlled") and gives
no automatic criterion. The schedule here is externally prescribed; no state
estimation or contact-driven inference is performed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Sequence, Tuple

import numpy as np

from .patterns import GeneralPattern, PatternDomainError

STAGES: Tuple[str, ...] = ("approach", "search", "align", "insert")

# Eq.(23)-(26): which unit patterns enter each stage command.
COMPOSITION: Dict[str, Tuple[str, ...]] = {
    "approach": ("push",),
    "search": ("push", "spiral"),
    "align": ("push", "wiggle", "rub"),
    "insert": ("push",),
}

# §V-C: the four documented assembly-case stage sequences.
CASES: Dict[str, Tuple[str, ...]] = {
    "case1_approach_search_align_insert": ("approach", "search", "align", "insert"),
    "case2_approach_search_insert": ("approach", "search", "insert"),
    "case3_approach_align_insert": ("approach", "align", "insert"),
    "case4_approach_insert": ("approach", "insert"),
}


class StageDomainError(ValueError):
    """Raised for unknown stages of invalid schedules."""


def stage_wrench(stage: str, patterns: Dict[str, GeneralPattern], t: float) -> np.ndarray:
    """Eq.(23)-(26) at time t: sum of the unit pattern wrenches for `stage`."""
    if stage not in COMPOSITION:
        raise StageDomainError(f"unknown stage: {stage!r}")
    missing = [name for name in COMPOSITION[stage] if name not in patterns]
    if missing:
        raise StageDomainError(f"stage {stage!r} requires patterns {missing}")
    total = np.zeros(6)
    for name in COMPOSITION[stage]:
        total = total + np.asarray(patterns[name].wrench(t), dtype=float)
    return total


@dataclass(frozen=True)
class Segment:
    stage: str
    t_start: float
    t_end: float


class StageSchedule:
    """Externally prescribed, contiguous, ordered stage schedule [ADAPTATION]."""

    def __init__(self, segments: Sequence[Segment]):
        if not segments:
            raise StageDomainError("schedule must contain at least one segment")
        checked = []
        previous_end = None
        for seg in segments:
            t0, t1 = float(seg.t_start), float(seg.t_end)
            if not (np.isfinite(t0) and np.isfinite(t1)):
                raise StageDomainError("segment boundaries must be finite")
            if t1 <= t0:
                raise StageDomainError(f"segment {seg.stage!r} has non-increasing time")
            if seg.stage not in COMPOSITION:
                raise StageDomainError(f"unknown stage in schedule: {seg.stage!r}")
            if previous_end is not None and abs(t0 - previous_end) > 1e-12:
                raise StageDomainError(
                    f"schedule is not contiguous at t={t0} (previous end {previous_end})")
            checked.append(Segment(seg.stage, t0, t1))
            previous_end = t1
        self.segments = tuple(checked)

    @property
    def t_start(self) -> float:
        return self.segments[0].t_start

    @property
    def t_end(self) -> float:
        return self.segments[-1].t_end

    @property
    def sequence(self) -> Tuple[str, ...]:
        return tuple(seg.stage for seg in self.segments)

    def segment_at(self, t: float) -> Segment:
        value = float(t)
        if not np.isfinite(value):
            raise StageDomainError("time must be finite")
        for seg in self.segments:
            if seg.t_start <= value < seg.t_end:
                return seg
        raise StageDomainError(
            f"time {value} outside schedule [{self.t_start}, {self.t_end})")

    def wrench_at(self, patterns: Dict[str, GeneralPattern], t: float) -> Tuple[str, np.ndarray]:
        seg = self.segment_at(t)
        return seg.stage, stage_wrench(seg.stage, patterns, t)

    def discontinuities(self, patterns: Dict[str, GeneralPattern], t_samples=None) -> Tuple[dict, ...]:
        """Report wrench jumps at stage boundaries instead of assuming illegality.

        A command jump is legitimate (different stage = different command); the
        reviewer requires it be *reported*, not silently smoothed.

        Primary metrics are dimensionally meaningful: ``jump_force_N`` (norm of
        the force-part difference, N) and ``jump_moment_Nm`` (norm of the
        moment-part difference, N*m). ``jump_mixed_l2_unphysical`` concatenates
        newtons and newton-metres; it is kept only as a labelled, unnormalized
        numerical diagnostic and must not be quoted as a physical quantity
        (review R3).
        """
        rows = []
        for left, right in zip(self.segments[:-1], self.segments[1:]):
            w_before = stage_wrench(left.stage, patterns, left.t_end)
            w_after = stage_wrench(right.stage, patterns, right.t_start)
            delta = w_after - w_before
            rows.append({
                "t_boundary_s": right.t_start,
                "from_stage": left.stage,
                "to_stage": right.stage,
                "jump_force_N": float(np.linalg.norm(delta[:3])),
                "jump_moment_Nm": float(np.linalg.norm(delta[3:])),
                "jump_mixed_l2_unphysical": float(np.linalg.norm(delta)),
            })
        return tuple(rows)


def schedule_from_case(case: str, boundaries: Sequence[float]) -> StageSchedule:
    """Build a schedule from a documented case sequence and prescribed boundaries.

    `boundaries` has len(sequence)+1 entries; stage i spans [b_i, b_{i+1}).
    """
    if case not in CASES:
        raise StageDomainError(f"unknown documented case: {case!r}")
    sequence = CASES[case]
    bounds = [float(b) for b in boundaries]
    if len(bounds) != len(sequence) + 1:
        raise StageDomainError(
            f"case {case!r} needs {len(sequence) + 1} boundaries, got {len(bounds)}")
    segments = [Segment(stage, bounds[i], bounds[i + 1])
                for i, stage in enumerate(sequence)]
    return StageSchedule(segments)
