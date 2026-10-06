import datetime
import os
import random
import re
import subprocess
import sys
import webbrowser as wb
from typing import Optional
from urllib.parse import quote_plus

import pyttsx3
import speech_recognition as sr
import wikipedia
import pyautogui
import pyjokes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NAME_FILE = os.path.join(BASE_DIR, "assistant_name.txt")
NOTES_FILE = os.path.join(BASE_DIR, "data.txt")

_engine = None


def get_engine():
    """Initialises the text-to-speech engine on first use."""
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
        voices = _engine.getProperty('voices')
        # Prefer the second (usually female) voice, but not every system has one.
        if len(voices) > 1:
            _engine.setProperty('voice', voices[1].id)
        _engine.setProperty('rate', 150)
        _engine.setProperty('volume', 1)
    return _engine


def speak(audio) -> None:
    engine = get_engine()
    engine.say(audio)
    engine.runAndWait()


def has_word(query: str, *words: str) -> bool:
    """Returns True if any of the given words/phrases appear as whole words in the query."""
    return any(re.search(rf"\b{re.escape(word)}\b", query) for word in words)


def time() -> None:
    """Tells the current time."""
    current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
    speak("The current time is")
    speak(current_time)
    print("The current time is", current_time)


def date() -> None:
    """Tells the current date."""
    now = datetime.datetime.now()
    speak("The current date is")
    speak(f"{now.day} {now.strftime('%B')} {now.year}")
    print(f"The current date is {now.day}/{now.month}/{now.year}")


def wishme() -> None:
    """Greets the user based on the time of day."""
    speak("Welcome back, sir!")
    print("Welcome back, sir!")

    hour = datetime.datetime.now().hour
    if 4 <= hour < 12:
        greeting = "Good morning!"
    elif 12 <= hour < 16:
        greeting = "Good afternoon!"
    else:
        greeting = "Good evening!"
    speak(greeting)
    print(greeting)

    assistant_name = load_name()
    speak(f"{assistant_name} at your service. Please tell me how may I assist you.")
    print(f"{assistant_name} at your service. Please tell me how may I assist you.")


def screenshot(name: Optional[str] = None) -> None:
    """Takes a screenshot and saves it, optionally with a custom filename."""
    pictures_dir = os.path.join(os.path.expanduser("~"), "Pictures")
    os.makedirs(pictures_dir, exist_ok=True)

    if name:
        name = re.sub(r"[^\w\- ]", "", name).strip().replace(" ", "_")
    if not name:
        name = datetime.datetime.now().strftime("screenshot_%Y%m%d_%H%M%S")

    img_path = os.path.join(pictures_dir, f"{name}.png")
    img = pyautogui.screenshot()
    img.save(img_path)
    speak(f"Screenshot saved as {name}.")
    print(f"Screenshot saved as {img_path}.")


def takecommand() -> Optional[str]:
    """Takes microphone input from the user and returns it as text.

    Falls back to keyboard input if no microphone (or PyAudio) is available.
    """
    r = sr.Recognizer()
    try:
        source = sr.Microphone()
    except (OSError, AttributeError):
        query = input("Type your command: ").strip()
        return query.lower() or None

    with source:
        print("Listening...")
        r.pause_threshold = 1

        try:
            audio = r.listen(source, timeout=5)  # Listen with a timeout
        except sr.WaitTimeoutError:
            speak("Timeout occurred. Please try again.")
            return None

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language="en-in")
        print(query)
        return query.lower()
    except sr.UnknownValueError:
        speak("Sorry, I did not understand that.")
        return None
    except sr.RequestError:
        speak("Speech recognition service is unavailable.")
        return None
    except Exception as e:
        speak(f"An error occurred: {e}")
        print(f"Error: {e}")
        return None


def open_file(path: str) -> None:
    """Opens a file with the default application on any OS."""
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def play_music(song_name=None) -> None:
    """Plays music from the user's Music directory."""
    song_dir = os.path.join(os.path.expanduser("~"), "Music")
    try:
        songs = os.listdir(song_dir)
    except FileNotFoundError:
        speak("I couldn't find your Music folder.")
        print(f"Music folder not found: {song_dir}")
        return

    if song_name:
        songs = [song for song in songs if song_name.lower() in song.lower()]

    if songs:
        song = random.choice(songs)
        open_file(os.path.join(song_dir, song))
        speak(f"Playing {song}.")
        print(f"Playing {song}.")
    else:
        speak("No song found.")
        print("No song found.")


def set_name() -> None:
    """Sets a new name for the assistant."""
    speak("What would you like to name me?")
    name = takecommand()
    if name:
        with open(NAME_FILE, "w") as file:
            file.write(name)
        speak(f"Alright, I will be called {name} from now on.")
    else:
        speak("Sorry, I couldn't catch that.")


def load_name() -> str:
    """Loads the assistant's name from a file, or uses a default name."""
    try:
        with open(NAME_FILE, "r") as file:
            return file.read().strip() or "Jarvis"
    except FileNotFoundError:
        return "Jarvis"  # Default name


def search_wikipedia(query):
    """Searches Wikipedia and returns a summary."""
    if not query:
        speak("What should I search on Wikipedia?")
        return
    try:
        speak("Searching Wikipedia...")
        result = wikipedia.summary(query, sentences=2)
        speak(result)
        print(result)
    except wikipedia.exceptions.DisambiguationError:
        speak("Multiple results found. Please be more specific.")
    except Exception:
        speak("I couldn't find anything on Wikipedia.")


def search_google(query) -> None:
    """Opens a Google search for the query in the default browser."""
    if not query:
        wb.open("https://www.google.com")
        return
    speak(f"Searching Google for {query}.")
    wb.open(f"https://www.google.com/search?q={quote_plus(query)}")


def remember(note) -> None:
    """Appends a note to the notes file."""
    if not note:
        speak("What should I remember?")
        note = takecommand()
    if not note:
        speak("Sorry, I couldn't catch that.")
        return
    with open(NOTES_FILE, "a") as file:
        file.write(note.strip() + "\n")
    speak(f"I'll remember that {note}.")


def recall() -> None:
    """Reads back saved notes."""
    try:
        with open(NOTES_FILE, "r") as file:
            notes = file.read().strip()
    except FileNotFoundError:
        notes = ""
    if notes:
        speak(f"You asked me to remember: {notes}")
        print(notes)
    else:
        speak("You haven't asked me to remember anything.")


def confirm(action: str) -> bool:
    """Asks the user to confirm a destructive action."""
    speak(f"Are you sure you want to {action}? Say yes to confirm.")
    answer = takecommand()
    return bool(answer) and has_word(answer, "yes", "yeah", "confirm")


def power_command(restart: bool) -> None:
    if sys.platform.startswith("win"):
        os.system("shutdown /r /f /t 1" if restart else "shutdown /s /f /t 1")
    else:
        os.system("shutdown -r now" if restart else "shutdown -h now")


def handle_query(query: str) -> bool:
    """Runs the command for a query. Returns False when the assistant should stop."""
    if has_word(query, "offline", "exit", "quit", "goodbye"):
        speak("Going offline. Have a good day!")
        return False

    elif "wikipedia" in query:
        search_wikipedia(query.replace("wikipedia", "").replace("search", "").strip())

    elif has_word(query, "search google", "google search", "search for"):
        search = re.sub(r"\b(search google for|search google|google search for|google search|search for)\b", "", query)
        search_google(search.strip())

    elif "play music" in query:
        play_music(query.replace("play music", "").strip())

    elif "open youtube" in query:
        wb.open("https://www.youtube.com")

    elif "open google" in query:
        wb.open("https://www.google.com")

    elif "change your name" in query:
        set_name()

    elif "screenshot" in query:
        name = query.split(" named ", 1)[1] if " named " in query else None
        screenshot(name)

    elif has_word(query, "joke"):
        joke = pyjokes.get_joke()
        speak(joke)
        print(joke)

    elif "do you remember" in query or "what did i ask you to remember" in query:
        recall()

    elif "remember that" in query:
        remember(query.split("remember that", 1)[1].strip())

    elif has_word(query, "time"):
        time()

    elif has_word(query, "date"):
        date()

    elif has_word(query, "shutdown", "shut down"):
        if confirm("shut down the system"):
            speak("Shutting down the system, goodbye!")
            power_command(restart=False)
            return False
        speak("Shutdown cancelled.")

    elif has_word(query, "restart"):
        if confirm("restart the system"):
            speak("Restarting the system, please wait!")
            power_command(restart=True)
            return False
        speak("Restart cancelled.")

    return True


if __name__ == "__main__":
    wishme()

    while True:
        query = takecommand()
        if not query:
            continue
        if not handle_query(query):
            break
