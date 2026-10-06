import os
import sys
import types
import unittest
from unittest import mock

# Stub out hardware/network dependent libraries so the tests run anywhere.
for name in ("pyttsx3", "speech_recognition", "wikipedia", "pyautogui", "pyjokes"):
    sys.modules.setdefault(name, mock.MagicMock())

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Jarvis"))
import jarvis  # noqa: E402


class HandleQueryTests(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(jarvis, "speak")
        self.speak = patcher.start()
        self.addCleanup(patcher.stop)

    def test_exit_stops_loop(self):
        self.assertFalse(jarvis.handle_query("go offline"))

    def test_time_is_whole_word(self):
        with mock.patch.object(jarvis, "time") as t:
            jarvis.handle_query("sometimes i wonder")
            t.assert_not_called()
            jarvis.handle_query("what is the time")
            t.assert_called_once()

    def test_update_does_not_trigger_date(self):
        with mock.patch.object(jarvis, "date") as d:
            jarvis.handle_query("check for update")
            d.assert_not_called()

    def test_google_search(self):
        with mock.patch.object(jarvis.wb, "open") as wb_open:
            jarvis.handle_query("search google for python tutorials")
            wb_open.assert_called_once_with("https://www.google.com/search?q=python+tutorials")

    def test_shutdown_requires_confirmation(self):
        with mock.patch.object(jarvis, "takecommand", return_value="no"), \
             mock.patch.object(jarvis, "power_command") as power:
            self.assertTrue(jarvis.handle_query("shutdown"))
            power.assert_not_called()

    def test_shutdown_confirmed(self):
        with mock.patch.object(jarvis, "takecommand", return_value="yes"), \
             mock.patch.object(jarvis, "power_command") as power:
            self.assertFalse(jarvis.handle_query("shutdown"))
            power.assert_called_once_with(restart=False)

    def test_screenshot_custom_name(self):
        with mock.patch.object(jarvis, "screenshot") as shot:
            jarvis.handle_query("take a screenshot named my desk")
            shot.assert_called_once_with("my desk")


class NotesTests(unittest.TestCase):
    def test_remember_and_recall(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp, \
             mock.patch.object(jarvis, "NOTES_FILE", os.path.join(tmp, "notes.txt")), \
             mock.patch.object(jarvis, "speak") as speak:
            jarvis.handle_query("remember that the meeting is at ten")
            jarvis.handle_query("do you remember anything")
            self.assertIn("the meeting is at ten", speak.call_args[0][0])


class EngineTests(unittest.TestCase):
    def test_single_voice_system(self):
        engine = mock.MagicMock()
        engine.getProperty.return_value = [types.SimpleNamespace(id="only")]
        with mock.patch.object(jarvis.pyttsx3, "init", return_value=engine), \
             mock.patch.object(jarvis, "_engine", None):
            jarvis.get_engine()
        voice_calls = [c for c in engine.setProperty.call_args_list if c[0][0] == "voice"]
        self.assertEqual(voice_calls, [])


if __name__ == "__main__":
    unittest.main()
