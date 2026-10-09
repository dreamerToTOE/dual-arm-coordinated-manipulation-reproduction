"""Pure launcher tests: no Isaac import, ROS, debugger inferior or physics."""
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "platforms/isaac_ros2/handoff/task01_startup_debug_launcher.py"
spec = importlib.util.spec_from_file_location("startup_guard", LAUNCHER)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class StartupGuardTests(unittest.TestCase):
    def test_frozen_original_anchor(self):
        source = LAUNCHER.with_name("task01_insert_ready_gui.py")
        self.assertEqual(module.validated_barrier(source), 125)

    def test_hash_mismatch_refuses(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "bad.py"
            source.write_text("raise RuntimeError('must not execute')\n")
            with self.assertRaisesRegex(RuntimeError, "hash mismatch"):
                module.validated_barrier(source)

    def test_ambiguous_anchor_refuses(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "bad.py"
            source.write_text("def main():\n    ns['_apply_official_joint_limits']()\n    ns['_apply_official_joint_limits']()\n    timeline.play()\n")
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            with self.assertRaisesRegex(RuntimeError, "Unique pre-control"):
                module.validated_barrier(source, digest)

    def test_real_exit_skips_anchor_and_finally(self):
        # Isolated stdlib Python process, not the Isaac interpreter/inferior.
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            source = path / "fake.py"
            source.write_text("def main():\n    try:\n        print('PREFIX', flush=True)\n        ns['_apply_official_joint_limits']()\n        timeline.play()\n    finally:\n        print('UNSAFE_FINALLY', flush=True)\nmain()\n")
            script = (
                "import importlib.util, pathlib, runpy, sys; "
                f"s=importlib.util.spec_from_file_location('guard',{str(LAUNCHER)!r}); "
                "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
                f"g=m.StartupGuard(pathlib.Path({str(source)!r}),4,pathlib.Path({str(path / 'guard.json')!r})); "
                "sys.settrace(g.trace); "
                f"runpy.run_path({str(source)!r})"
            )
            result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 42, result.stderr)
            self.assertIn("PREFIX", result.stdout)
            self.assertIn("PRE_CONTROL_BARRIER_STOP", result.stdout)
            self.assertNotIn("UNSAFE_FINALLY", result.stdout)

    def test_early_exception_stops_before_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            source = path / "fake.py"
            source.write_text("def main():\n    try:\n        raise ValueError('early')\n        ns['_apply_official_joint_limits']()\n        timeline.play()\n    finally:\n        print('UNSAFE_FINALLY', flush=True)\nmain()\n")
            script = (
                "import importlib.util, pathlib, runpy, sys; "
                f"s=importlib.util.spec_from_file_location('guard',{str(LAUNCHER)!r}); "
                "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
                f"g=m.StartupGuard(pathlib.Path({str(source)!r}),4,pathlib.Path({str(path / 'guard.json')!r})); "
                "sys.settrace(g.trace); "
                f"runpy.run_path({str(source)!r})"
            )
            result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 43, result.stderr)
            self.assertIn("UNEXPECTED_CONTROL_FLOW_STOP", result.stdout)
            self.assertNotIn("UNSAFE_FINALLY", result.stdout)


if __name__ == "__main__":
    unittest.main()
