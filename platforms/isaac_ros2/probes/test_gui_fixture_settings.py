"""[ENGINEERING] GUI显示约定；无Isaac/机器人命令。"""
import unittest
from task01_cube04_headless import simulation_settings


class GuiSettingsTest(unittest.TestCase):
    def test_visible_mode_cannot_be_headless(self):
        config = simulation_settings(True)
        self.assertIs(config['headless'], False)
        self.assertIn('--/exts/isaacsim.code_editor.vscode/host=127.0.0.1', config['extra_args'])
        self.assertNotIn('--no-window', config['extra_args'])

    def test_historical_settings_remain_reproducible(self):
        self.assertIs(simulation_settings(False)['headless'], True)


if __name__ == '__main__':
    unittest.main()
