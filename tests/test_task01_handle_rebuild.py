"""[ENGINEERING] Pure mock tests of static original-handle rebuild guards.

No SimulationApp, engine, GUI, stage construction, or physics integration.
Run: python3 -m unittest discover -s tests -p test_task01_handle_rebuild.py -v
These tests do not certify original model initialization or collision parity.
"""

import ast
from pathlib import Path
import runpy
import unittest


PROBE = Path(__file__).resolve().parents[1] / "platforms/isaac_ros2/probes/task01_single_cube_model_parity_gui.py"
HELPERS = runpy.run_path(str(PROBE), run_name="task01_handle_rebuild_test_helpers")
DISPATCH = "/app/player/playSimulations"


class Settings:
    def __init__(self, original=True):
        self.value = original
        self.writes = []

    def get(self, path):
        if path != DISPATCH:
            raise AssertionError("Only original dispatcher setting may be read here")
        return self.value

    def set_bool(self, path, value):
        if path != DISPATCH or not isinstance(value, bool):
            raise AssertionError("Only exact dispatcher bool may be written")
        self.writes.append(value)
        self.value = value


class Timeline:
    playing = False
    time = 0.0

    def is_playing(self):
        return self.playing

    def get_current_time(self):
        return self.time


class View:
    def __init__(self, harness, name):
        self.harness = harness
        self.name = name
        self.count = 1
        self.valid = True

    def check(self):
        self.harness.call("check:" + self.name)
        return self.valid


class NewSimulation:
    def __init__(self, harness):
        self.harness = harness
        self.device_ordinal = -1
        self.views = {"left": View(harness, "left"), "right": View(harness, "right"),
                      "Cube": View(harness, "Cube")}

    def set_subspace_roots(self, pattern):
        self.harness.call("subspace:" + pattern)

    def create_articulation_view(self, path):
        side = {"/World/left_fr3": "left", "/World/right_fr3": "right"}[path]
        self.harness.call("art:" + side)
        return self.views[side]

    def create_rigid_body_view(self, path):
        if path != "/World/Task01/Cube":
            raise AssertionError("Must recreate only original Cube handle")
        self.harness.call("body:Cube")
        return self.views["Cube"]


class Harness:
    def __init__(self, original=True):
        self.settings = Settings(original)
        self.timeline = Timeline()
        self.physics_steps = []
        self.digest = "immutable-original"
        self.calls = []
        self.actions = {}
        self.new = NewSimulation(self)
        harness = self

        class OldSimulation:
            def invalidate(self):
                harness.call("invalidate")

        class Physx:
            def release_physics_objects(self):
                harness.call("release")

            def force_load_physics_from_usd(self):
                harness.call("force_load")

            def start_simulation(self):
                harness.call("start")

        class Tensors:
            def create_simulation_view(self, frontend):
                if frontend != "numpy":
                    raise AssertionError("Must recreate original CPU numpy backend")
                harness.call("tensor:numpy")
                return harness.new

        self.old = OldSimulation()
        self.physx = Physx()
        self.tensors = Tensors()

    def call(self, name):
        if self.settings.value is not False:
            raise AssertionError("Dispatcher must remain disabled throughout rebuild")
        self.calls.append(name)
        if name in self.actions:
            self.actions[name]()

    def rebuild(self):
        return HELPERS["rebuild_original_static_handles"](
            self.physx, self.tensors, self.old, self.settings, self.timeline,
            self.physics_steps, "immutable-original", lambda: self.digest)


class HandleRebuildTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()

    def assert_rejected_and_restored(self):
        original = self.h.settings.value
        with self.assertRaises(RuntimeError):
            self.h.rebuild()
        self.assertIs(self.h.settings.value, original)

    def test_exact_original_rebuild_order_and_views(self):
        sim, arts, cube = self.h.rebuild()
        self.assertEqual(self.h.calls, ["invalidate", "release", "force_load", "start",
                                      "tensor:numpy", "subspace:/", "art:left", "art:right",
                                      "body:Cube", "check:left", "check:right", "check:Cube"])
        self.assertIs(sim, self.h.new)
        self.assertIs(arts["left"], self.h.new.views["left"])
        self.assertIs(arts["right"], self.h.new.views["right"])
        self.assertIs(cube, self.h.new.views["Cube"])
        self.assertEqual(self.h.settings.writes, [False, True])

    def test_false_original_dispatcher_stays_false(self):
        self.h = Harness(False)
        self.h.rebuild()
        self.assertIs(self.h.settings.value, False)
        self.assertEqual(self.h.settings.writes, [False, False])

    def test_initial_model_mismatch_rejected_before_invalidation(self):
        self.h.digest = "changed"
        self.assert_rejected_and_restored()
        self.assertEqual(self.h.calls, [])

    def test_initial_playing_or_callback_rejected_before_invalidation(self):
        self.h.timeline.playing = True
        self.assert_rejected_and_restored()
        self.assertEqual(self.h.calls, [])
        self.h.timeline.playing = False
        self.h.physics_steps.append(0.0)
        self.assert_rejected_and_restored()
        self.assertEqual(self.h.calls, [])

    def test_non_finite_initial_clock_rejected_before_invalidation(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                self.h = Harness()
                self.h.timeline.time = value
                self.assert_rejected_and_restored()
                self.assertEqual(self.h.calls, [])

    def test_missing_or_non_bool_original_dispatcher_rejected(self):
        for value in (None, 0, 1, "true"):
            with self.subTest(value=value):
                self.h = Harness(value)
                self.assert_rejected_and_restored()
                self.assertEqual(self.h.calls, [])
                self.assertEqual(self.h.settings.writes, [])

    def test_release_must_not_roll_back_original_usd_model(self):
        self.h.actions["release"] = lambda: setattr(self.h, "digest", "rolled-back")
        self.assert_rejected_and_restored()
        self.assertEqual(self.h.calls, ["invalidate", "release"])

    def test_callback_during_release_stops_before_reparse_and_keeps_dt(self):
        self.h.actions["release"] = lambda: self.h.physics_steps.append(1.0 / 60.0)
        self.assert_rejected_and_restored()
        self.assertEqual(self.h.calls, ["invalidate", "release"])
        self.assertEqual(self.h.physics_steps, [1.0 / 60.0])

    def test_start_must_not_integrate_or_change_clock(self):
        for change in ("callback", "time", "playing", "model"):
            with self.subTest(change=change):
                self.h = Harness()
                action = {"callback": lambda: self.h.physics_steps.append(0.0),
                          "time": lambda: setattr(self.h.timeline, "time", 1.0 / 60.0),
                          "playing": lambda: setattr(self.h.timeline, "playing", True),
                          "model": lambda: setattr(self.h, "digest", "changed")}[change]
                self.h.actions["start"] = action
                self.assert_rejected_and_restored()
                self.assertNotIn("tensor:numpy", self.h.calls)

    def test_native_or_tensor_exception_restores_exact_dispatcher(self):
        for original in (True, False):
            for at in ("invalidate", "release", "force_load", "start", "tensor:numpy", "check:Cube"):
                with self.subTest(original=original, at=at):
                    self.h = Harness(original)
                    def fail():
                        raise ValueError("simulated SDK exception")
                    self.h.actions[at] = fail
                    with self.assertRaisesRegex(ValueError, "simulated SDK exception"):
                        self.h.rebuild()
                    self.assertIs(self.h.settings.value, original)

    def test_invalid_view_or_count_rejected(self):
        for name in ("left", "right", "Cube"):
            for bad_count in (0, 2):
                with self.subTest(name=name, count=bad_count):
                    self.h = Harness()
                    self.h.new.views[name].count = bad_count
                    self.assert_rejected_and_restored()
            with self.subTest(name=name, valid=False):
                self.h = Harness()
                self.h.new.views[name].valid = False
                self.assert_rejected_and_restored()

    def test_gpu_backend_rejected_not_silently_adapted(self):
        for ordinal in (0, 1):
            with self.subTest(ordinal=ordinal):
                self.h = Harness()
                self.h.new.device_ordinal = ordinal
                self.assert_rejected_and_restored()

    def test_final_view_creation_guard_rejects_time_callback_and_model_changes(self):
        for change in ("callback", "time", "playing", "model"):
            with self.subTest(change=change):
                self.h = Harness()
                action = {"callback": lambda: self.h.physics_steps.append(1.0 / 60.0),
                          "time": lambda: setattr(self.h.timeline, "time", 1.0 / 60.0),
                          "playing": lambda: setattr(self.h.timeline, "playing", True),
                          "model": lambda: setattr(self.h, "digest", "changed")}[change]
                self.h.actions["check:Cube"] = action
                self.assert_rejected_and_restored()
                self.assertEqual(self.h.calls[-1], "check:Cube")


class StaticRebuildSourceContractTests(unittest.TestCase):
    def test_no_replay_reset_play_step_or_jointstate_schema(self):
        tree = ast.parse(PROBE.read_text())
        calls = [n.func.attr for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
        for prohibited in ("reset_simulation", "play", "update_simulation", "simulate", "fetch_results"):
            self.assertNotIn(prohibited, calls)
        self.assertFalse(any(isinstance(n, ast.Attribute) and n.attr == "JointStateAPI"
                             for n in ast.walk(tree)))
        helper = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                      and n.name == "rebuild_original_static_handles")
        helper_calls = [n.func.attr for n in ast.walk(helper)
                        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
        self.assertNotIn("set_dof_positions", helper_calls)
        self.assertNotIn("set_transforms", helper_calls)


if __name__ == "__main__":
    unittest.main()
