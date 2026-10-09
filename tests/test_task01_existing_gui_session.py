"""[ENGINEERING] Pure lifecycle tests; no SDK/ROS import or physical execution.

AST comparison establishes source preservation, not Isaac runtime acceptance.
Only the two stdlib-only precondition functions are compiled into mock contexts.
"""
import ast
import hashlib
import json
import math
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "platforms/isaac_ros2/handoff"
ADAPTER = HANDOFF / "task01_existing_gui_session.py"
ORIGINAL = HANDOFF / "task01_insert_ready_gui.py"
ADAPTER_TREE = ast.parse(ADAPTER.read_text(encoding="utf-8"))
ORIGINAL_TREE = ast.parse(ORIGINAL.read_text(encoding="utf-8"))


def function(tree, name):
    matches = [node for node in ast.walk(tree)
               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
               and node.name == name]
    if len(matches) != 1:
        raise AssertionError(f"Expected one {name} function, found {len(matches)}")
    return matches[0]


def calls(tree):
    return [node for node in ast.walk(tree) if isinstance(node, ast.Call)]


def call_name(call):
    node = call.func
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = ast.unparse(node.value)
        return prefix + "." + node.attr
    return ast.unparse(node)


def dict_literals(tree, key):
    result = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            result.extend(value for name, value in zip(node.keys, node.values)
                          if isinstance(name, ast.Constant) and name.value == key)
    return result


def guard_namespace():
    selected = [function(ADAPTER_TREE, name)
                for name in ("require_scene_state", "require_bridge_state", "require_callback_state")]
    # Deliberately do not import the module: its sampler/bridge dependencies
    # belong to Isaac and are outside this pure software test's authority.
    namespace = {"sha": Mock(return_value="approved-config"),
                 "SCENE_KEY": "task01_existing_gui_scene_token"}
    code = compile(ast.Module(body=selected, type_ignores=[]), str(ADAPTER), "exec")
    exec(code, namespace)
    return namespace


class SceneStateTests(unittest.TestCase):
    def setUp(self):
        self.namespace = guard_namespace()
        self.guard = self.namespace["require_scene_state"]
        self.timeline = SimpleNamespace(is_stopped=Mock(return_value=True))
        self.stage = object()

    def test_stop_accepts_without_mutating_session(self):
        self.assertIsNone(self.guard(self.timeline, self.stage))
        self.timeline.is_stopped.assert_called_once_with()
        self.namespace["sha"].assert_not_called()

    def test_pause_is_not_stop(self):
        self.timeline.is_stopped.return_value = False
        with self.assertRaisesRegex(RuntimeError, "Pause"):
            self.guard(self.timeline, self.stage)

    def test_missing_stage_refuses(self):
        with self.assertRaises(RuntimeError):
            self.guard(self.timeline, None)

    def test_active_bridge_refuses_even_when_stopped(self):
        with self.assertRaisesRegex(RuntimeError, "bridge"):
            self.guard(self.timeline, self.stage, active=True)


class BridgeStateTests(unittest.TestCase):
    def setUp(self):
        self.namespace = guard_namespace()
        self.guard = self.namespace["require_bridge_state"]
        self.timeline = SimpleNamespace(is_playing=Mock(return_value=True))
        self.prim = SimpleNamespace(GetCustomDataByKey=Mock(return_value="scene-token"))
        self.stage = SimpleNamespace(GetDefaultPrim=Mock(return_value=self.prim))
        self.context = {"stage": self.stage, "token": "scene-token",
                        "config_path": Path("approved-benchmark.yaml"),
                        "config_sha256": "approved-config"}
        self.sim = object()

    def test_play_live_view_stage_and_hash_accept(self):
        self.assertIsNone(self.guard(self.timeline, self.stage, self.context, self.sim))
        self.prim.GetCustomDataByKey.assert_called_once_with(self.namespace["SCENE_KEY"])
        self.namespace["sha"].assert_called_once_with(self.context["config_path"])

    def test_not_playing_refuses_before_hash_check(self):
        self.timeline.is_playing.return_value = False
        with self.assertRaisesRegex(RuntimeError, "Play"):
            self.guard(self.timeline, self.stage, self.context, self.sim)
        self.namespace["sha"].assert_not_called()

    def test_missing_live_view_refuses(self):
        with self.assertRaisesRegex(RuntimeError, "Play"):
            self.guard(self.timeline, self.stage, self.context, None)

    def test_missing_scene_context_refuses(self):
        with self.assertRaisesRegex(RuntimeError, "Stage"):
            self.guard(self.timeline, self.stage, None, self.sim)

    def test_different_stage_refuses(self):
        with self.assertRaisesRegex(RuntimeError, "Stage"):
            self.guard(self.timeline, object(), self.context, self.sim)
        self.namespace["sha"].assert_not_called()

    def test_stage_token_mismatch_refuses(self):
        self.prim.GetCustomDataByKey.return_value = "another-scene"
        with self.assertRaisesRegex(RuntimeError, "Stage"):
            self.guard(self.timeline, self.stage, self.context, self.sim)
        self.namespace["sha"].assert_not_called()

    def test_config_hash_change_refuses(self):
        self.namespace["sha"].return_value = "changed-config"
        with self.assertRaisesRegex(RuntimeError, "benchmark changed"):
            self.guard(self.timeline, self.stage, self.context, self.sim)


class CallbackLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.namespace = guard_namespace()
        self.guard = self.namespace["require_callback_state"]
        self.timeline = SimpleNamespace(is_playing=Mock(return_value=True))
        self.prim = SimpleNamespace(GetCustomDataByKey=Mock(return_value="scene-token"))
        self.stage = SimpleNamespace(GetDefaultPrim=Mock(return_value=self.prim))
        self.context = {"stage": self.stage, "token": "scene-token"}

    def test_callback_accepts_current_playing_stage(self):
        self.assertIsNone(self.guard(self.timeline, self.stage, self.context))
        self.namespace["sha"].assert_not_called()

    def test_callback_refuses_interrupted_timeline(self):
        self.timeline.is_playing.return_value = False
        with self.assertRaisesRegex(RuntimeError, "Timeline interrupted"):
            self.guard(self.timeline, self.stage, self.context)

    def test_callback_refuses_different_stage(self):
        with self.assertRaisesRegex(RuntimeError, "Stage changed"):
            self.guard(self.timeline, object(), self.context)

    def test_callback_refuses_changed_token(self):
        self.prim.GetCustomDataByKey.return_value = "unrelated-scene"
        with self.assertRaisesRegex(RuntimeError, "Stage changed"):
            self.guard(self.timeline, self.stage, self.context)

    def callback_namespace(self, name):
        bridge = SimpleNamespace(halted=False, pre_step=Mock())
        namespace = dict(self.namespace, timeline=self.timeline, context=self.context,
                         omni=SimpleNamespace(usd=SimpleNamespace(get_context=lambda:
                             SimpleNamespace(get_stage=lambda: self.stage))),
                         bridge=bridge, errors=[], contacts=[], math=math,
                         halt_callback=Mock(), on_post_step=Mock(), contact_stream=Mock())
        namespace["contacts"] = Mock(clear=Mock())
        tree = ast.Module(body=[function(ADAPTER_TREE, name)], type_ignores=[])
        exec(compile(tree, str(ADAPTER), "exec"), namespace)
        return namespace

    def test_pre_step_checks_identity_before_any_control(self):
        namespace = self.callback_namespace("pre_step")
        self.timeline.is_playing.return_value = False
        namespace["pre_step"](1 / 60)
        namespace["contacts"].clear.assert_not_called()
        namespace["bridge"].pre_step.assert_not_called()
        namespace["halt_callback"].assert_called_once()

    def test_pre_step_preserves_fixed_dt_gate(self):
        namespace = self.callback_namespace("pre_step")
        namespace["pre_step"](1 / 30)
        namespace["bridge"].pre_step.assert_not_called()
        namespace["halt_callback"].assert_called_once()
        self.assertIn("Unexpected physics dt", str(namespace["halt_callback"].call_args.args[0]))

    def test_valid_pre_step_uses_original_bridge(self):
        namespace = self.callback_namespace("pre_step")
        namespace["pre_step"](1 / 60)
        namespace["bridge"].pre_step.assert_called_once_with(1 / 60)
        namespace["halt_callback"].assert_not_called()

    def test_post_step_checks_identity_before_sampling(self):
        namespace = self.callback_namespace("post_step")
        self.prim.GetCustomDataByKey.return_value = "different-scene"
        namespace["post_step"](1 / 60)
        namespace["on_post_step"].assert_not_called()
        namespace["contact_stream"].write.assert_not_called()
        namespace["halt_callback"].assert_called_once()

    def test_stop_snapshot_preserves_last_native_stamp_without_mutation(self):
        latest = {"physics_step": 17, "simulation_stamp_ns": 283333334,
                  "frame_id": "world", "phase": "FIXED_HANDOFF"}
        snapshot_pub = Mock()
        namespace = {"latest": latest, "snapshot_pub": snapshot_pub, "json": json,
                     "String": lambda **kwargs: SimpleNamespace(**kwargs)}
        tree = ast.Module(body=[function(ADAPTER_TREE, "publish_stop_snapshot")], type_ignores=[])
        exec(compile(tree, str(ADAPTER), "exec"), namespace)
        namespace["publish_stop_snapshot"]("Stage changed")
        stopped = json.loads(snapshot_pub.publish.call_args.args[0].data)
        self.assertEqual(stopped, dict(latest, halted=True, error="Stage changed"))
        self.assertNotIn("halted", latest)
        namespace["latest"] = {}
        snapshot_pub.reset_mock()
        namespace["publish_stop_snapshot"]("no native sample")
        snapshot_pub.publish.assert_not_called()


class SourceContractTests(unittest.TestCase):
    def test_no_standalone_or_manual_physics_lifecycle(self):
        forbidden_names = {"SimulationApp", "new_stage", "simulate", "fetch_results",
                           "fetchResults", "app.update", "app.close", "timeline.play"}
        for call in calls(ADAPTER_TREE):
            name = call_name(call)
            self.assertNotIn(name, forbidden_names)
            if isinstance(call.func, ast.Attribute):
                self.assertNotIn(call.func.attr,
                                 {"new_stage", "simulate", "fetch_results", "fetchResults"})
        for node in ast.walk(ADAPTER_TREE):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                self.assertFalse(any(item.name == "SimulationApp" for item in node.names))

    def test_scene_only_builds_and_never_sends_control(self):
        scene_calls = {call_name(call) for call in calls(function(ADAPTER_TREE, "load_scene"))}
        self.assertTrue({"require_scene_state", "original_constructor_namespace"} <= scene_calls)
        self.assertFalse(scene_calls & {"restore", "start_bridge", "bridge._command",
                                        "bridge.pre_step", "timeline.play"})

    def test_scene_constructs_exactly_one_benchmark_cube(self):
        cube_calls = [call for call in calls(function(ADAPTER_TREE, "load_scene"))
                      if call_name(call) == "box" and call.args
                      and isinstance(call.args[0], ast.Constant)
                      and call.args[0].value == "/World/Task01/Cube"]
        self.assertEqual(len(cube_calls), 1)
        keywords = {entry.arg: ast.literal_eval(entry.value) for entry in cube_calls[0].keywords}
        self.assertEqual(keywords, {"dynamic": True, "gravity": True})

    def test_config_and_standalone_harness_fingerprints_unchanged(self):
        benchmark = ROOT / "configs/benchmark/benchmark_v1.yaml"
        self.assertEqual(hashlib.sha256(benchmark.read_bytes()).hexdigest(),
                         "25b7162c848b4cfeeff7e07a8cd154f26dff215c6d8f3d1caf8cf6333bcc8783")
        self.assertEqual(hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(),
                         "539615dc789460abc2e3b0b2e7c09dff8c7ad00b8dc74327f1e8d114a0a1a77c")

    def test_scene_and_bridge_editor_entrypoints_are_separate(self):
        scene = ast.parse((HANDOFF / "task01_existing_gui_scene.py").read_text())
        bridge = ast.parse((HANDOFF / "task01_existing_gui_bridge.py").read_text())
        self.assertEqual([call_name(node.value) for node in scene.body
                          if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)],
                         ["load_scene"])
        start_calls = [call for call in calls(bridge) if call_name(call) == "start_bridge"]
        self.assertEqual(len(start_calls), 1)
        self.assertFalse(any(call_name(call) == "load_scene" for call in calls(bridge)))
        keywords = {entry.arg: ast.literal_eval(entry.value) for entry in start_calls[0].keywords}
        self.assertEqual(keywords, {"wall_limit_sec": 180.0, "launch_driver": False})

    def test_bridge_default_does_not_launch_driver_or_reset(self):
        start = function(ADAPTER_TREE, "start_bridge")
        defaults = dict(zip([arg.arg for arg in start.args.args][-len(start.args.defaults):],
                            start.args.defaults))
        self.assertIs(ast.literal_eval(defaults["launch_driver"]), False)
        self.assertEqual(ast.literal_eval(defaults["wall_limit_sec"]), 180.0)
        namespace_calls = [call for call in calls(start) if call_name(call) == "SimpleNamespace"]
        self.assertEqual(len(namespace_calls), 1)
        reset = [entry.value for entry in namespace_calls[0].keywords if entry.arg == "reset_repeats"]
        self.assertEqual([ast.literal_eval(value) for value in reset], [0])

    def test_bridge_guard_precedes_evidence_and_task_creation(self):
        start = function(ADAPTER_TREE, "start_bridge")
        by_name = {call_name(call): call.lineno for call in calls(start)}
        for effect in ("args.output_dir.mkdir", "write_json", "asyncio.ensure_future"):
            self.assertLess(by_name["require_bridge_state"], by_name[effect])

    def test_pre_post_callbacks_retain_explicit_native_order(self):
        subscriptions = [call for call in calls(ADAPTER_TREE)
                         if call_name(call) == "physx.subscribe_physics_on_step_events"]
        self.assertEqual(len(subscriptions), 2)
        self.assertEqual([(ast.unparse(call.args[0]), ast.literal_eval(call.args[1]),
                           ast.literal_eval(call.args[2])) for call in subscriptions],
                         [("pre_step", True, 0), ("post_step", False, 200)])

    def test_pre_post_callbacks_guard_before_effects(self):
        for name, effect in (("pre_step", "bridge.pre_step"), ("post_step", "on_post_step")):
            callback_calls = {call_name(call): call.lineno
                              for call in calls(function(ADAPTER_TREE, name))}
            self.assertLess(callback_calls["require_callback_state"], callback_calls[effect])

    def test_external_driver_is_observed_not_assumed_successful(self):
        run = function(ADAPTER_TREE, "run_session")
        seen_checks = [node for node in ast.walk(run) if isinstance(node, ast.If)
                       and ast.unparse(node.test) == "not external_driver_seen"]
        self.assertEqual(len(seen_checks), 1)
        self.assertIsInstance(seen_checks[0].body[0], ast.Raise)
        observed_updates = [node for node in ast.walk(run) if isinstance(node, ast.AugAssign)
                            and ast.unparse(node.target) == "external_driver_seen"]
        self.assertEqual(len(observed_updates), 1)
        self.assertIn("node.get_node_names_and_namespaces()", ast.unparse(observed_updates[0].value))
        external_exit_waits = [node for node in ast.walk(run) if isinstance(node, ast.While)
                               and "node.get_node_names_and_namespaces()" in ast.unparse(node.test)]
        self.assertEqual(len(external_exit_waits), 1)
        exit_codes = dict_literals(run, "external_driver_exit_code")
        self.assertEqual(len(exit_codes), 1)
        self.assertIsInstance(exit_codes[0], ast.IfExp)
        self.assertEqual(ast.unparse(exit_codes[0].test), "process is None")
        self.assertEqual(ast.literal_eval(exit_codes[0].body), "NOT_OBSERVED")

    def test_optional_owned_launch_keeps_readback_evidence_parameter(self):
        run = function(ADAPTER_TREE, "run_session")
        guarded = [node for node in ast.walk(run) if isinstance(node, ast.If)
                   and ast.unparse(node.test) == "args.launch_driver"]
        self.assertEqual(len(guarded), 1)
        self.assertIn("readback_evidence_dir:=", ast.unparse(guarded[0]))
        self.assertIn("planning_world_readback", ast.unparse(guarded[0]))

    def test_post_step_state_sampler_ast_matches_original(self):
        self.assertEqual(ast.dump(function(ADAPTER_TREE, "on_post_step"), include_attributes=False),
                         ast.dump(function(ORIGINAL_TREE, "on_post_step"), include_attributes=False))

    def test_metadata_excludes_target_force_and_frozen_claims(self):
        for key in ("TARGET_execution", "force_calibration", "FROZEN"):
            values = dict_literals(ADAPTER_TREE, key)
            self.assertTrue(values, key)
            self.assertTrue(all(isinstance(value, ast.Constant) and value.value is False
                                for value in values), key)
        statuses = dict_literals(ADAPTER_TREE, "task01_status")
        self.assertTrue(statuses)
        self.assertEqual({ast.literal_eval(value) for value in statuses}, {"PARTIAL"})
        self.assertFalse(any("task27" in call_name(call).lower() for call in calls(ADAPTER_TREE)))


if __name__ == "__main__":
    unittest.main()
