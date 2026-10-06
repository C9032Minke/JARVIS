import json
import os
import sys
import types
import unittest
from unittest import mock

for name in ("pyttsx3", "speech_recognition", "wikipedia", "pyautogui", "pyjokes"):
    sys.modules.setdefault(name, mock.MagicMock())

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Jarvis"))
import brain  # noqa: E402
import jarvis  # noqa: E402


class FakeAnthropic:
    """Minimal stand-in for the anthropic module's error classes."""
    class AnthropicError(Exception):
        pass

    class APIStatusError(AnthropicError):
        pass

    class APIConnectionError(AnthropicError):
        pass

    class AuthenticationError(APIStatusError):
        pass


def make_response(payload, stop_reason="end_turn"):
    block = types.SimpleNamespace(type="text", text=json.dumps(payload))
    return types.SimpleNamespace(stop_reason=stop_reason, content=[block])


def make_brain(response=None, error=None):
    b = brain.Brain.__new__(brain.Brain)
    b.enabled = True
    b.history = []
    b.system = "test"
    b.client = mock.MagicMock()
    if error:
        b.client.beta.messages.create.side_effect = error
    else:
        b.client.beta.messages.create.return_value = response
    return b


@mock.patch.object(brain, "anthropic", FakeAnthropic)
class InterpretTests(unittest.TestCase):
    def test_returns_command_and_records_history(self):
        payload = {"intent": "wikipedia", "argument": "Alexander Graham Bell", "reply": ""}
        b = make_brain(make_response(payload))
        self.assertEqual(b.interpret("who invented the telephone"), payload)
        self.assertEqual([m["role"] for m in b.history], ["user", "assistant"])

    def test_request_shape(self):
        b = make_brain(make_response({"intent": "joke", "argument": "", "reply": ""}))
        b.interpret("make me laugh")
        kwargs = b.client.beta.messages.create.call_args.kwargs
        self.assertEqual(kwargs["output_config"]["format"]["type"], "json_schema")
        self.assertEqual(kwargs["fallbacks"], "default")
        self.assertNotIn("tool_choice", kwargs)

    def test_refusal_falls_back(self):
        b = make_brain(make_response({}, stop_reason="refusal"))
        self.assertIsNone(b.interpret("anything"))
        self.assertEqual(b.history, [])

    def test_unknown_intent_falls_back(self):
        b = make_brain(make_response({"intent": "launch_rocket", "argument": "", "reply": ""}))
        self.assertIsNone(b.interpret("launch the rocket"))

    def test_connection_error_keeps_ai_enabled(self):
        b = make_brain(error=FakeAnthropic.APIConnectionError("offline"))
        self.assertIsNone(b.interpret("hello"))
        self.assertTrue(b.enabled)

    def test_auth_error_disables_ai(self):
        b = make_brain(error=FakeAnthropic.AuthenticationError("bad key"))
        self.assertIsNone(b.interpret("hello"))
        self.assertFalse(b.enabled)

    def test_missing_credentials_disables_ai(self):
        b = make_brain(error=TypeError("Could not resolve authentication method"))
        self.assertIsNone(b.interpret("hello"))
        self.assertFalse(b.enabled)

    def test_history_is_capped(self):
        b = make_brain(make_response({"intent": "chat", "argument": "", "reply": "hi"}))
        for _ in range(30):
            b.interpret("hello")
        self.assertEqual(len(b.history), brain.MAX_HISTORY_MESSAGES)
        self.assertEqual(b.history[0]["role"], "user")


class HandleQueryWithBrainTests(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(jarvis, "speak")
        self.speak = patcher.start()
        self.addCleanup(patcher.stop)

    def brain_returning(self, command):
        b = mock.MagicMock()
        b.interpret.return_value = command
        return b

    def test_chat_reply_is_spoken(self):
        b = self.brain_returning({"intent": "chat", "argument": "", "reply": "Paris."})
        self.assertTrue(jarvis.handle_query("capital of france", b))
        self.speak.assert_called_with("Paris.")

    def test_ai_intent_is_run(self):
        b = self.brain_returning({"intent": "google_search", "argument": "weather", "reply": ""})
        with mock.patch.object(jarvis, "search_google") as search:
            jarvis.handle_query("is it going to rain", b)
            search.assert_called_once_with("weather")

    def test_ai_shutdown_still_needs_confirmation(self):
        b = self.brain_returning({"intent": "shutdown", "argument": "", "reply": ""})
        with mock.patch.object(jarvis, "takecommand", return_value="no"), \
             mock.patch.object(jarvis, "power_command") as power:
            self.assertTrue(jarvis.handle_query("turn off the computer", b))
            power.assert_not_called()

    def test_falls_back_to_keywords(self):
        b = self.brain_returning(None)
        with mock.patch.object(jarvis, "time") as t:
            jarvis.handle_query("what's the time", b)
            t.assert_called_once()

    def test_open_website_adds_scheme(self):
        b = self.brain_returning({"intent": "open_website", "argument": "github.com", "reply": ""})
        with mock.patch.object(jarvis.wb, "open") as wb_open:
            jarvis.handle_query("open github", b)
            wb_open.assert_called_once_with("https://github.com")


if __name__ == "__main__":
    unittest.main()
