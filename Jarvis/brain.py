"""Natural-language command understanding for Jarvis, powered by Claude.

Turns free-form speech like "could you look up who invented the telephone"
into one of Jarvis's commands, and answers general questions conversationally.
If the Anthropic SDK isn't installed, no credentials are configured, or the
API can't be reached, interpret() returns None and Jarvis falls back to its
built-in keyword matching.
"""

import json
import os
from typing import Optional

try:
    import anthropic
except ImportError:  # The AI brain is optional.
    anthropic = None

MODEL = os.environ.get("JARVIS_MODEL", "claude-opus-5-5")
MAX_HISTORY_MESSAGES = 20

INTENTS = {
    "time": "Tell the current time.",
    "date": "Tell the current date.",
    "wikipedia": "Look up a person, place or topic on Wikipedia. argument: the topic.",
    "google_search": "Search Google. argument: the search terms.",
    "open_website": "Open a website. argument: a full https:// URL.",
    "play_music": "Play music from the Music folder. argument: song name, or empty for any song.",
    "remember": "Save a note for later. argument: the note text.",
    "recall": "Read back the user's saved notes.",
    "screenshot": "Take a screenshot. argument: a filename if the user gave one, else empty.",
    "joke": "Tell a joke.",
    "change_name": "Rename the assistant.",
    "shutdown": "Shut down the computer.",
    "restart": "Restart the computer.",
    "exit": "Stop the assistant / go offline.",
    "chat": "Anything else: greetings, questions, small talk. Put the spoken answer in reply.",
}

SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {"type": "string", "enum": list(INTENTS)},
        "argument": {"type": "string"},
        "reply": {"type": "string"},
    },
    "required": ["intent", "argument", "reply"],
    "additionalProperties": False,
}

SYSTEM_PROMPT = """You are the brain of {name}, a desktop voice assistant. \
Each user message is a transcription of something the user said out loud, \
so expect speech-recognition mistakes and read it for what the user meant.

Map the request to exactly one of these intents:
{intents}

Rules:
- Pick a device intent only when the user is asking you to do that thing now. \
"I need to restart my thinking" is chat, not restart.
- For chat, reply in one to three short, natural sentences: the reply is read \
aloud, so no markdown, lists, URLs or emoji.
- For every other intent, leave reply empty unless a short spoken \
acknowledgement adds something.
- Leave argument empty when an intent takes none."""


class Brain:
    def __init__(self, assistant_name: str = "Jarvis"):
        self.enabled = anthropic is not None and os.environ.get("JARVIS_AI", "1") != "0"
        self.client = anthropic.Anthropic() if self.enabled else None
        self.history = []
        intents = "\n".join(f"- {name}: {desc}" for name, desc in INTENTS.items())
        self.system = SYSTEM_PROMPT.format(name=assistant_name, intents=intents)

    def interpret(self, query: str) -> Optional[dict]:
        """Returns {"intent", "argument", "reply"} for the query, or None to fall back to keywords."""
        if not self.enabled:
            return None

        messages = self.history + [{"role": "user", "content": query}]
        try:
            response = self.client.beta.messages.create(
                model=MODEL,
                max_tokens=2048,
                system=self.system,
                messages=messages,
                output_config={
                    "effort": "low",  # Keep spoken responses snappy.
                    "format": {"type": "json_schema", "schema": SCHEMA},
                },
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            )
        except anthropic.AuthenticationError:
            print("AI brain disabled: invalid Anthropic credentials.")
            self.enabled = False
            return None
        except (anthropic.APIStatusError, anthropic.APIConnectionError) as e:
            print(f"AI brain unavailable, using keyword commands: {e}")
            return None
        except (anthropic.AnthropicError, TypeError) as e:
            # The SDK raises TypeError when no credentials are configured at all.
            print(f"AI brain disabled, using keyword commands: {e}")
            self.enabled = False
            return None

        if response.stop_reason != "end_turn":
            return None
        text = next((b.text for b in response.content if b.type == "text"), "")
        try:
            command = json.loads(text)
        except json.JSONDecodeError:
            return None
        if command.get("intent") not in INTENTS:
            return None

        self.history = (messages + [{"role": "assistant", "content": text}])[-MAX_HISTORY_MESSAGES:]
        return command
