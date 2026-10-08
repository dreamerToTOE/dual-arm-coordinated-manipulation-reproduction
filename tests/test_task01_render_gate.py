"""[ENGINEERING] Pure mock render-dispatch regression; never starts Isaac.

Run: python3 -m unittest discover -s tests -p test_task01_render_gate.py -v
Passing these software guards is not evidence of scene-query or model parity.
"""

from pathlib import Path
import runpy
import unittest


PROBE = Path(__file__).resolve().parents[1] / "platforms/isaac_ros2/probes/task01_single_cube_model_parity_gui.py"
HELPERS = runpy.run_path(str(PROBE), run_name="task01_render_gate_test_helpers")
SETTING = "/app/player/playSimulations"


class Settings:
    def __init__(self, original=True):
        self.value = original
        self.writes = []

    def get(self, path):
        if path != SETTING:
            raise AssertionError("Render gate may not touch physics/model settings")
        return self.value

    def set_bool(self, path, value):
        if path != SETTING or not isinstance(value, bool):
            raise AssertionError("Expected only an exact dispatcher bool write")
        self.writes.append((path, value))
        self.value = value


class Timeline:
    def __init__(self, playing=False, current_time=0.0):
        self.playing = playing
        self.current_time = current_time

    def is_playing(self):
        return self.playing

    def get_current_time(self):
        return self.current_time


class App:
    def __init__(self, settings, action=None):
        self.settings = settings
        self.action = action
        self.updates = 0

    def update(self):
        self.updates += 1
        if self.settings.value is not False:
            raise AssertionError("Physics dispatcher must be disabled during app.update")
        if self.action:
            self.action()


class StaticRenderGateTests(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()
        self.timeline = Timeline()
        self.physics_steps = []
        self.app = App(self.settings)

    def render(self):
        return HELPERS["static_render_update"](
            self.app, self.timeline, self.settings, self.physics_steps)

    def assert_rejected_with_restored_setting(self):
        original = self.settings.value
        with self.assertRaises(RuntimeError):
            self.render()
        self.assertIs(self.settings.value, original)

    def test_original_true_restored_after_render_only_update(self):
        self.render()
        self.assertIs(self.settings.value, True)
        self.assertEqual(self.settings.writes, [(SETTING, False), (SETTING, True)])
        self.assertEqual(self.app.updates, 1)
        self.assertEqual(self.physics_steps, [])
        self.assertEqual(self.timeline.current_time, 0.0)

    def test_original_false_preserved_not_unconditionally_enabled(self):
        self.settings.value = False
        self.render()
        self.assertIs(self.settings.value, False)
        self.assertEqual(self.settings.writes, [(SETTING, False), (SETTING, False)])

    def test_repeated_render_calls_preserve_original_dispatcher(self):
        for _ in range(3):
            self.render()
        self.assertEqual(self.app.updates, 3)
        self.assertIs(self.settings.value, True)
        self.assertEqual(self.physics_steps, [])

    def test_app_exception_restores_true_in_finally(self):
        def fail():
            raise ValueError("simulated rendering failure")
        self.app.action = fail
        with self.assertRaisesRegex(ValueError, "simulated rendering failure"):
            self.render()
        self.assertIs(self.settings.value, True)
        self.assertEqual(self.settings.writes[-1], (SETTING, True))

    def test_app_exception_restores_false_in_finally(self):
        self.settings.value = False
        def fail():
            raise ValueError("simulated rendering failure")
        self.app.action = fail
        with self.assertRaises(ValueError):
            self.render()
        self.assertIs(self.settings.value, False)

    def test_already_playing_rejected_before_update(self):
        self.timeline.playing = True
        self.assert_rejected_with_restored_setting()
        self.assertEqual(self.app.updates, 0)
        self.assertEqual(self.settings.writes, [])

    def test_existing_physics_callback_rejected_before_update(self):
        self.physics_steps.append(1.0 / 60.0)
        self.assert_rejected_with_restored_setting()
        self.assertEqual(self.app.updates, 0)
        self.assertEqual(self.settings.writes, [])
        self.assertEqual(self.physics_steps, [1.0 / 60.0])

    def test_callback_during_render_rejected_and_dt_preserved(self):
        self.app.action = lambda: self.physics_steps.append(1.0 / 60.0)
        self.assert_rejected_with_restored_setting()
        self.assertEqual(self.app.updates, 1)
        self.assertEqual(self.physics_steps, [1.0 / 60.0])

    def test_zero_dt_callback_is_still_a_real_callback_and_rejected(self):
        self.app.action = lambda: self.physics_steps.append(0.0)
        self.assert_rejected_with_restored_setting()
        self.assertEqual(self.physics_steps, [0.0])

    def test_timeline_advancement_rejected_without_physics_callback(self):
        self.app.action = lambda: setattr(self.timeline, "current_time", 1.0 / 60.0)
        self.assert_rejected_with_restored_setting()
        self.assertEqual(self.physics_steps, [])

    def test_timeline_rewind_is_also_rejected(self):
        self.timeline.current_time = 0.5
        self.app.action = lambda: setattr(self.timeline, "current_time", 0.0)
        self.assert_rejected_with_restored_setting()

    def test_queued_play_without_integration_rejected_after_render(self):
        self.app.action = lambda: setattr(self.timeline, "playing", True)
        self.assert_rejected_with_restored_setting()
        self.assertEqual(self.app.updates, 1)

    def test_missing_or_non_boolean_setting_rejected_before_write(self):
        for value in (None, 0, 1, "false", "true"):
            with self.subTest(value=value):
                self.settings = Settings(value)
                self.app = App(self.settings)
                self.assert_rejected_with_restored_setting()
                self.assertEqual(self.settings.writes, [])
                self.assertEqual(self.app.updates, 0)

    def test_non_finite_initial_time_rejected_before_update(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                self.timeline = Timeline(current_time=value)
                self.settings = Settings()
                self.app = App(self.settings)
                self.assert_rejected_with_restored_setting()
                self.assertEqual(self.app.updates, 0)

    def test_non_finite_time_created_during_render_rejected(self):
        self.app.action = lambda: setattr(self.timeline, "current_time", float("nan"))
        self.assert_rejected_with_restored_setting()


if __name__ == "__main__":
    unittest.main()
