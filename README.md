# Jarvis Desktop Voice Assistant🔥

<img src="https://giffiles.alphacoders.com/212/212508.gif" alt="">

**Have you ever wondered how cool it would be to have your own assistant? Imagine how easier it would be doing Wikipedia searches without opening web browsers, and performing many other daily tasks like playing music with the help of a single voice command, opening different browsers in just a voice command.**

**This project is simple desktop voice assistant built with python named as “Jarvis Desktop Voice Assistant”. This project is fully completed and error free. It was compiled in VS Code Editor.**

**🔸 Let's be honest, it's not as intelligent as in the movie, but it can do a lot of cool things and automate your daily tasks you do on your personal computers/laptops.**

## 📌Built with

<code><img height="30" src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/python/python.png"></code>

## 📌Features

It can do a lot of cool things, some of them being:

- Greet user
- Tell current time and date
- Launch applications/softwares
- Open any website
- Tells about any person (via Wikipedia)
- Can search anything on Google
- Plays music
- Take important notes in a text file and read them back
- Can take screenshot and save it with custom filename
- Can tell jokes
- Shut down / restart the computer (asks for confirmation first)
- Falls back to keyboard input when no microphone is available
- Works on Windows, macOS and Linux

## 📌Smarter Commands with Claude (optional)

By default Jarvis matches keywords, so you have to say commands fairly precisely. If you give it an
[Anthropic API key](https://console.anthropic.com/), Jarvis uses Claude to understand what you
*mean* instead:

- Say things naturally: *"could you look up who invented the telephone"*, *"is it going to rain today"*,
  *"pull up github"*. Claude picks the right command for you.
- Ask anything else (*"what's the capital of Australia?"*, *"how do I boil an egg?"*) and Jarvis answers out loud.
- Jarvis remembers the last few exchanges, so follow-ups like *"how old is he?"* work.
- Shutdown and restart still ask you to confirm.

To turn it on, set your key before running Jarvis:

```bash
export ANTHROPIC_API_KEY=your-key-here      # macOS/Linux
set ANTHROPIC_API_KEY=your-key-here         # Windows (cmd)
```

Without a key, or when you're offline, Jarvis automatically falls back to keyword matching. Set
`JARVIS_AI=0` to force keyword mode, or `JARVIS_MODEL` to use a different Claude model
(default: `claude-opus-5-5`). Each command is one API request, which is billed to your Anthropic account.

## 📌Voice Commands

These keyword commands always work, with or without an API key:

| Say… | Jarvis will… |
|------|--------------|
| "what's the **time**" / "what's the **date**" | Tell the current time or date |
| "**wikipedia** Alan Turing" | Read a two-sentence Wikipedia summary |
| "**search google for** python tutorials" | Open a Google search in your browser |
| "**open youtube**" / "**open google**" | Open the website |
| "**play music** [song name]" | Play a (matching) song from your `Music` folder |
| "**remember that** I have a meeting at 10" | Save a note to `Jarvis/data.txt` |
| "**do you remember** anything" | Read your saved notes back |
| "take a **screenshot** [named my desk]" | Save a screenshot to your `Pictures` folder |
| "tell me a **joke**" | Tell a programming joke |
| "**change your name**" | Rename the assistant |
| "**shutdown**" / "**restart**" | Power off / restart after you say "yes" |
| "go **offline**" / "**exit**" | Stop the assistant |

## Requirements

Python 3.6+

## 📌Installation

1. **Fork The Repository**
   - Click the "Fork" button on the top right corner of the repository page.

2. **Clone The Repository**
   - Clone the forked repository to your local machine:
     ```bash
     git clone <URL>
     cd JARVIS
     ```

3.  **Create and Activate a Virtual Environment**
     - Create a virtual environment:
     ```bash
     python -m venv .venv
     ```
   - Activate the virtual environment:
     - For Windows:
       ```bash
       .venv\Scripts\activate
       ```
     - For macOS/Linux:
       ```bash
       source .venv/bin/activate
       ```
   - This activates the virtual environment and should look like `(venv) directory/of/your/project>`

4. **Install Requirements**

   - Install all the requirements given in **[requirements.txt](https://github.com/kishanrajput23/Jarvis-Desktop-Voice-Assistant/blob/main/requirements.txt)** by running the command `pip install -r requirements.txt`

5. **PyAudio troubleshooting** (needed for the microphone)
   - PyAudio is included in `requirements.txt`. If it fails to install:
     - Windows: see **[here](https://stackoverflow.com/questions/52283840/i-cant-install-pyaudio-on-windows-how-to-solve-error-microsoft-visual-c-14)**
     - macOS: `brew install portaudio` then retry
     - Linux: `sudo apt install portaudio19-dev` then retry
   - Without a working microphone, Jarvis falls back to typed commands.

6. **Run the Assistant**
  - Run the main script:
    ```bash
    python Jarvis/jarvis.py
    ```
  - Now Enjoy with your own assistant !!!!

7. **Deactivate the Virtual Environment**
   - After you're done, deactivate the virtual environment:
     ```bash
     deactivate
     ```

## 📌Running Tests

The tests mock the microphone, speech and GUI libraries, so they run anywhere:

```bash
python -m unittest discover -s tests
```

## 📌Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📌Author

👤 **Kishan Kumar Rai**

- Twitter: [@kishan_rajput23](https://twitter.com/kishan_rajput23)
- Github: [@kishanrajput23](https://github.com/kishanrajput23)
- LinkedIn: [@kishan-kumar-rai](https://linkedin.com/in/kishan-kumar-rai-23112000)

## 📌Show your support

Please ⭐️ this repository if this project helped you!

## 📌License

This project is [MIT](https://choosealicense.com/licenses/mit/) licensed.

## 📌Learning Resources to Extend This Project

To build this project further and enhance its capabilities, a strong understanding of the following areas is recommended:

### 🐍 Python Fundamentals
Python is the core language behind this project. A solid grasp of syntax, control flow, functions, and error handling will help you modify and extend the assistant’s functionality.  
👉 [Python Programming Course](https://www.mygreatlearning.com/academy/premium/master-python-programming)

### 🎙️ Voice Processing & NLP
Voice commands are processed using speech and text-based techniques. Understanding Natural Language Processing (NLP) concepts such as tokenization and text analysis can help improve voice interaction.  
👉 [Introduction to NLP](https://www.mygreatlearning.com/academy/learn-for-free/courses/introduction-to-natural-language-processing)

### 🤖 Intelligence & Generative AI
Currently, the assistant follows predefined logic. By integrating Generative AI concepts, it can be enhanced into a conversational assistant capable of generating intelligent responses and performing web-based tasks.  
👉 [Introduction to Generative AI](https://www.mygreatlearning.com/academy/premium/master-generative-ai)

### 👁️ Computer Vision
To make the assistant more advanced, computer vision can be introduced for features like face detection and gesture control. Learning image and video processing fundamentals is a good starting point.  
👉 [Computer Vision Essentials](https://www.mygreatlearning.com/academy/learn-for-free/courses/computer-vision-essentials)

### 📄 Related Reading
For a conceptual overview of building voice assistants in Python, you can refer to this article: [CLICK HERE](https://www.mygreatlearning.com/blog/jarvis-desktop-assistant-python-project/)

---

> *Some learning resources mentioned above are shared as part of an educational collaboration.*
