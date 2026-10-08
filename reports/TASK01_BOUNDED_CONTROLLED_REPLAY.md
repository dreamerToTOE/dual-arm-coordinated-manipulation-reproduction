# TASK01 — Bounded Critical-State Controlled Replay Fallback

2026-10-08. **PARTIAL — one approved bounded attempt used; STOP FOR USER**. The PRE section below is the preserved source-checkpoint plan, not a new run authorization.

## PRE-TASK REPORT

- Task: TASK01 remaining Tier2 critical safety / deterministic reset evidence.
- Scientific objective: minimum reproducible one-Cube common benchmark, not simulator model equivalence.
- Minimum sufficient evidence: no obvious unexpected Isaac collision invalidating approved nominal geometry at four recorded critical states; then five measured deterministic resets each at START/PRE_PUSH, all with post-physics simulation time.
- Current scope: **START/state0, PRE_PUSH/state135, state196/B60, TARGET/state292 only**; not all292 states. No replacements needed: TARGET already contains the minimum wrist/tool–environment FCL distance2.212219mm, state196 the minimum all-pair0.999669mm.
- Explicit non-goals: zero-step/query-tree/native-handle repairs, parity10, equivalence proof, continuous collision proof, suction stability, wrench/force controller, P2/P3, five-Cube Task27, target/time/success-tolerance redesign.
- Attempt budget: prior07/08/09 same-root3/3 exhausted and permanently stopped; **one separately user-approved bounded controlled fallback**, no automatic repair/retry. Visible process cap120s (internal elapsed guard100s).
- Preferred method: original static-query route STOPPED; not reactivated.
- Approved fallback: original constructors/assets, exact recorded14q/Cube, one normal PhysX simulate/fetch step per snapshot, original contact reports (points/separations) and focused original shape/environment overlaps. Normal startup, not repeated native-handle reconstruction. No random IK or geometry/physics/ACM change.
- Stop/escalation: first explicit unexpected penetration/overlap, invalid state/contact reading, extra uncontrolled step, timeout or engineering failure stops this attempt. Preserve evidence; no new variant without user decision.
- Files expected: this minimal harness/test, run metadata/evidence, three TASK01 reports and six persistent records. Historical parity scripts remain unchanged.
- Validation: input hashes and four indices; pure contact-classification tests; source checkpoint before one visible run; q/Cube pre-write readback and same-poststep actual q/Cube/TCP/carriage/time; critical gate before reset; record5+5 if gate reached.
- Known ambiguities: reset/success numerical tolerances still PENDING_USER_REVIEW. Do not silently use IK tolerances for dynamic reset acceptance. Free dynamic Cube keeps original gravity; no claim of sustained held/suction state. TARGET Cube/deep-wall boundary is expected pending benchmark-definition review, not automatic collision FAIL.
- Execution drift review: each critical state and each first reset pauses at a stdin barrier after saving actual post-step q/Cube/TCP, drift and Cube/environment plane gaps. The executing agent must inspect these data before accepting the snapshot/advancing; no implicit numeric success tolerance is introduced. TARGET expected-boundary classification is not a waiver of actual deep penetration; actual gaps/contact separations are recorded and reviewed. Rejected/unclear snapshot stops the bounded run, not a new repair.
- Need user confirmation: no; this exact fallback authorized. FROZEN and any benchmark-definition change still require user.

## Paper fidelity

[ADAPTATION] unchanged dual-FR3 scientific benchmark. [ENGINEERING] bounded normal-step evidence gathering. [EXPERIMENTAL] simulator safety/reset observations only, not reproduced paper results. No paper controller, [DEVIATION], or benchmark redesign implemented.

## Intended command

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
timeout --signal=TERM --kill-after=20s 120s env DISPLAY=:1 PYTHONUNBUFFERED=1 \
  scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_critical_controlled_replay_gui.py \
  --output-dir results/20261008_TASK01_bounded_controlled_replay/raw \
  >results/20261008_TASK01_bounded_controlled_replay/launch.log 2>&1
```

Status is based on structured actual evidence, never wrapper exit0 alone. No second simulator run is automatically authorized.

## Actual single attempt

Source checkpoint `47d22ce3cc8a61f89cfaace5c2a9b3eab1e88ef8`, SHA256 `ab1748840559e8e4cbed33ab194d5c70fd118dc15a6951d5d094e4195c740dc8`. Historical parity09 source SHA remains `803b1e9e…`, unchanged. One visible GUI launch only, command above. One original dt normal `simulate/fetch` completed; post-step callback and native core agree at step1 / `0.01666666753590107 s`.

The first START measurement was saved, but the newly added stdin execution-review barrier did not consume the agent's `accept_snapshot` input. Read-only process inspection observed owned `python.sh` in `T` and Python in `Tl`, consistent with a background terminal-read/SIGTTIN stop under GNU timeout's default separate process group. This is a launcher/review workflow error, not a demonstrated physics/query failure or collision. Signal tracing was not captured, so the SIGTTIN explanation is an inference. At120s the launcher returned **124**, all owned processes were reaped. No internal `failure.json` or `summary.json` exists; [run_outcome.json](../results/20261008_TASK01_bounded_controlled_replay/run_outcome.json) is explicitly a post-run audit, not fabricated probe output.

**Do not rerun this command automatically.** A command-only foreground-terminal correction could address this launch issue, but it was not implemented/tested and no second attempt is authorized. No source modification or new simulator run followed the timeout.

## Saved scientific evidence — START only

| Quantity | Measured value |
|---|---:|
| Recorded critical-state indices sampled | 0 only; no135/196/292 |
| Pre-sync maximum14q readback error | 9.706288e-8 rad |
| Pre-sync Cube pose position error | 1.283923e-8 m |
| Post-sync max joint reset error | 9.050200e-5 rad |
| Largest joint change during step | 9.059906e-5 rad |
| Left/right TCP position error | 0.096015 / 0.067458 mm |
| Cube before / after world Z | 0.3799999952 / 0.3772749901 m |
| Cube translation / rotation during step | 2.725005 mm / 0 rad |
| Original contact reports | 8 cup–Cube headers,32 points, all positive separation |
| Minimum reported separation | +0.999954 mm; not penetration |
| Focus original-shape overlaps | 17queries,37hits;0 environment hits,0 callback/count errors |
| Unexpected collision evidence in saved sample | 0 |
| START/PRE reset repetitions | 0 / 0 |

Actual14q, Cube/TCP poses, all body poses, original shape hits and exact contact paths are preserved in [critical_START_sample.json](../results/20261008_TASK01_bounded_controlled_replay/critical_START_sample.json), unaltered SHA `959e6a70…`. Measured Cube mass0.8000000119kg/material0.5/0.5/0.0, originalgravity9.81/TGS/CCD/60Hz. Carriage frame `(0.910,0,0.200)` with identity rotation; identical before/after. Runtimeoriginalgeometry/source/benchmarkYAML/ACM/independentIK limits unchanged. [Metadata](../results/20261008_TASK01_bounded_controlled_replay/metadata.json), [actual launch log](../results/20261008_TASK01_bounded_controlled_replay/launch.log).

Do not label this CPU PhysX from the NumPy frontend: actual scene attributes are `enableGPUDynamics=True`, `broadphaseType=GPU`, as saved in scene_audit. These attributes are reported without changing them; no execution-device equivalence claim is made.

The Cube had **no active shared-held/suction constraint** in this short safety measurement and fell under original gravity. The2.725mm drift is not hidden/reset away; this sample must not be presented as stable-held Benchmark-A READY or as a valid repeated reset result. The execution-review acceptance was not recorded. For the minimum safety question, only the saved START neighborhood has positive evidence; PRE_PUSH, state196 and TARGET remain untested. Neither geometry infeasibility nor four-state safety is established by the launcher timeout.

## Definition items retained for the eventual candidate review

- TARGET Cube/deep-wall boundary-touch policy (not tested here; coordinates unchanged).
- Numeric READY/reset and later method success tolerances, currently PENDING_USER_REVIEW.
- Already-shared-held start semantics versus this short free-dynamic-Cube measurement; no suction-stability proof requested/provided.
- Physics60Hz versus candidate command100Hz policy, unchanged; no controller-frequency redesign.
- BUG019 original STL/convex-hull discrepancy remains a known limitation, not RESOLVED or equivalence-certified.
- BUG001 TCP/wrench/gravity-inertia calibration remains DEFERRED TASK10-IS, not a reason to extend TASK01.

## POST-TASK REPORT

- Task/status: TASK01 **PARTIAL**, approved bounded fallback stopped; no PASS CANDIDATE REVIEW/FROZEN.
- Scientific objective/minimum sufficient evidence achieved: unchanged nominal discrete geometry yes; four-state safety + repeated reset **no**.
- Completed/files: one minimal reuse-based normal-step harness;7 pure classification tests; frozen execution source and saved START same-step evidence; run outcome/metadata; three reports, task and six records updated.
- Commands/results:7 testsOK (software only); one120s capped visible launch exit124,1 physics step/START sample; actual state/contact and source/input hash audit; no following experiment.
- TASK-BLOCKING: remaining three critical safety states + repeated reset acceptance evidence; launcher prevents completion of the approved attempt.
- DEFERRED: BUG001/TASK10-IS wrench and later P2/P3 work.
- KNOWN LIMITATION: full model-equivalence/zero-step route stopped; free-Cube sample is not heldREADY proof; numeric benchmark decisions pending review.
- LEGACY: five-Cube Task27 remains outside current gate.
- Attempt budget: static07/08/09 same-root3/3 remains exhausted; separately approved one controlled GUI attempt1/1 used. Escalation required **yes**; no automatic retry or variant.
- Fidelity: [ADAPTATION] unchanged dualFR3 benchmark; [ENGINEERING] bounded normal-step diagnostic and records; [EXPERIMENTAL] one short measured snapshot only; [ORIGINAL] no reproduced controller claim; [DEVIATION] no benchmark/controller redesign.
- Records: STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS/USER_FEEDBACK updated, historical attempts preserved.
- Next action: STOP FOR USER. A further command-only rerun would require an explicit new bounded allowance; no parity10/query-tree/native-handle repair.
- Git: branch `task01-benchmark-draft`; source47d22ce; pre-existing untracked01/02logs preserved; cloud publication status recorded separately after push verification.

Git formatting note: the verbatim actual launch log ends in a prompt with a trailing space. This evidence byte stream is intentionally not reformatted; source/docs/JSON diff checks pass with that log excluded. Its original SHA is retained.

## ENGINEERING ESCALATION

- Scientific question: do the four approved critical states provide minimum Isaac safety evidence, followed by reproducible START/PRE resets?
- Already established: nominal A136/B157 geometry; exact recorded14q; one genuine START post-step snapshot with no observed unexpected penetration/environment overlap.
- Remaining unknown: safety at PRE/state196/TARGET and all repeated reset results. The unconstrained short-step Cube sample is not stable-held READY evidence.
- Why it matters: a single sample cannot replace the user-approved four-state/reset gate, especially at the2.212mm FCL wrist–wall minimum.
- Attempts: static root07/08/09 exhausted3/3; approved controlled GUI allowance used1/1, stopped at the added terminal review barrier, not a physics collision.
- Root blocker classification: TASK-BLOCKING acceptance-evidence gap; terminal review is an engineering method failure. Query perfection/model equivalence remains KNOWN LIMITATION.
- Is it still task-critical: missing acceptance evidence yes; perfecting zero-step queries no.
- Lower-cost evidence: the same existing controlled harness with a foreground-compatible bounded terminal launch, not a new probe/model/control layer. This remains untested and unapproved for a second run.
- Recommended action: STOP FOR USER; request one command-only bounded rerun allowance, retain all previous evidence and constraints.
- Need user decision: whether to authorize that additional attempt. No autonomous retry, benchmark redefinition or FROZEN.

## Git publication

Initial push was rejected because the remote task branch had new user governance commits, not because GitHub authentication failed. Read those five governance files completely, fetched and merged `bfd09ac` without conflicts or overwriting either history. The resulting `b73e273` (includes source47d22ce and evidence2cc95eb) was pushed successfully to `task01-benchmark-draft`; the GitHub file tool read back the new metadata with actual PARTIAL/exit124. Main was not changed. The earlier governance review9f5a03b is now uploaded as well. No source/config or new experiment accompanied the governance merge/publication.
