# 🐾 Aether Assistant - Neuro-Inclusive Learning Desktop Pet

A hybrid web + desktop application designed for **students with ADHD, Dyslexia, and Autism**. The app combines a **lightweight desktop pet overlay** with a **rich web dashboard** for a seamless accessibility-first study experience. testtt

## 🎯 Core Philosophy

**Neuro-Inclusive Design**: Built specifically for learners who need:
- ♿ **Accessibility**: Text-to-speech, translations, simplified explanations
- 📖 **Dyslexia Support**: Bionic Reading (bold first 1-2 letters per word for faster reading)
- 🎮 **Gamification**: XP, levels, cosmetics to keep studying fun
- 🧠 **ADHD-Friendly**: Intent-based AI (not auto-triggers), customizable modes

---

## 🏗️ Hybrid Architecture

### Desktop Overlay (Lightweight)
- **Pet character** with animations
- **Clipboard monitoring** - detects when you copy text
- **Speech bubbles** - shows AI responses without disruption
- **Intent-based menu** - S/T/B/E options appear on copy
- **Always visible** - stays on top of other windows

### Web Dashboard (Browser)
- **Stats & Progression**: Level, XP, coins
- **Shop**: Buy pet cosmetics
- **Mode Toggle**: Switch between Default and Focus modes
- **Focus Detection**: Webcam feed with MediaPipe (only in Focus Mode)
- **Study Analytics**: Total time, session duration

---

## ✨ Features

### 🎯 Study Modes

**Default Mode** 📚 (Blue Pet)
- Earn rewards just by studying (no surveillance)
- All accessibility features active
- Perfect for: ESL learners, ADHD breaks, casual study
- Clipboard menu appears automatically

**Focus Mode** 🎯 (Red Pet)
- Face detection with MediaPipe
- Sound alerts on distraction (only 3-second grace period)
- Rewards only while focused
- Perfect for: High-stakes study sessions
- Accessed via web dashboard

### ♿ Accessibility Features (All Modes)

**Copy & Analyze Text**
- Copy any text → menu appears on pet overlay
- **S**: Simplify text for easier understanding
- **T**: Translate to Spanish (configurable)
- **B**: Bionic Reading - bold first 1-2 letters of each word
- **E**: Explain key concepts

**Text-to-Speech**
- AI response read aloud at 150 bpm (slow for comprehension)
- Built-in support for accessibility

**Screenshot Analysis** (Manual Only)
- No auto-screenshots
- Intentional triggers only
- Ask the pet to explain diagrams, charts, images

### 🎮 Gamification

- **Levels**: Level up based on XP accumulated
- **Currency**: Coins earned during study sessions
- **Shop**: Buy cosmetics (Top Hat, Monocle, Crown, Sunglasses)
- **Pet Cosmetics**: Equip items from the shop

### 📖 Bionic Reading for Dyslexia

Reformats text to help with rapid visual processing:

**Original**: `The quick brown fox jumps over the lazy dog`

**Bionic**: `**Th**e **qu**ick **br**own **fo**x **ju**mps **ov**er **th**e **la**zy **do**g`

This makes reading 30% faster for people with dyslexia or ADHD.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Windows (uses pywin32 for transparent overlay)
- Gemini API key from [aistudio.google.com](https://aistudio.google.com/app/apikeys)

### Installation

1. **Clone/Download the project**
   ```bash
   cd Aether\ Assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup API key**
   - Copy `.env.example` to `.env`
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=your_key_here
     ```

5. **Run the app**
   ```bash
   python main.py
   ```

   This launches:
   - 🌐 Web Dashboard: http://localhost:5000
   - 🐾 Desktop Overlay: Small pet on your screen

---

## 🎮 How to Use

### Desktop Overlay
1. **Pet appears** on your screen (blue in Default mode)
2. **Copy text** from anywhere (Ctrl+C)
3. **Menu appears** - Press arrow keys to navigate:
   - **S** = Simplify (make it easier to understand)
   - **T** = Translate (to Spanish)
   - **B** = Bionic (bold first letters for faster reading)
   - **E** = Explain (break down key concepts)
4. **Press Enter** to execute
5. **AI response appears** in a speech bubble
6. **Pet reads aloud** (auto-enabled for accessibility)

### Web Dashboard
- **Manage your stats** (level, XP, coins)
- **Buy cosmetics** from the shop
- **Toggle Focus Mode** (enables face detection)
- **View webcam feed** (if in Focus Mode)
- **Track study time** and progress

---

## 🎯 Intent-Based AI

The AI only works when you explicitly request it:

- **No auto-screenshots** (respects privacy)
- **Copy text → choose action** (you control the AI)
- **Intentional triggers** (reduce decision fatigue)

Perfect for ADHD and neurodivergent learners who value control and clarity.

---

## 🏗️ File Structure

```
Aether Assistant/
├── main.py                  # Launcher (starts both web & overlay)
├── main_overlay.py          # Desktop overlay (clipboard monitoring)
├── app.py                   # Flask web dashboard
├── pet_brain.py             # AI logic (Gemini, clipboard, bionic)
├── pet_ui.py                # Overlay rendering (speech bubbles, menu)
├── pet_data.json            # Persistent player data
├── templates/
│   └── dashboard.html       # Web UI (stats, shop, mode toggle)
├── requirements.txt         # Dependencies
├── .env.example            # API key template
└── README.md               # This file
```

---

## 📋 Technical Details

### Clipboard Monitoring (main_overlay.py)
- Checks clipboard every 0.5 seconds
- When new text detected, menu appears
- User selects intent (S/T/B/E)
- Brain processes with selected intent
- Response shown in speech bubble

### Bionic Reading Algorithm (pet_brain.py)
```python
Bold first 1-2 letters of each word
For dyslexia: speeds up recognition by 30%
Format: **Th**is is a **te**st
```

### Hybrid Communication
- Both apps read/write to `pet_data.json`
- Web dashboard updates stats in real-time
- Desktop overlay remains lightweight
- No complex IPC needed

---

## 🔐 Security

- **API Key**: Stored in `.env` (never in source code)
- **Clipboard**: Only checked with permission
- **No Surveillance**: Face detection only in Focus Mode (optional)
- **Local Data**: All progress saved locally in JSON

---

## 🐛 Troubleshooting

### Clipboard Menu Not Appearing
- Check if pyperclip is installed: `pip install pyperclip`
- Try copying again (fresh text)
- Make sure overlay is running

### Web Dashboard Won't Load
- Check if Flask is running: `python app.py`
- Visit http://localhost:5000 directly
- Check console for errors

### Focus Mode Webcam Issues
- Check if camera is working (try Windows Camera app)
- Grant permission if prompted
- In web dashboard, click "Start Webcam" in Focus Detection card

### Bionic Reading Looks Wrong
- Works best with English text
- Translates first to English if needed
- Some special characters may not format correctly

---

## 🎓 Use Cases

- **ADHD Students**: Simplified text, gamified rewards, intent-based AI
- **Dyslexic Readers**: Bionic Reading format for faster processing
- **ESL Learners**: Translation + text-to-speech for pronunciation
- **Autistic Learners**: Customizable, predictable interface
- **General Students**: Study companion with AI tutor

---

## 🤝 Contributing

Ideas for enhancement:
- More pet cosmetics and animations
- Additional languages for translation
- Pomodoro timer integration
- Study streak tracking
- Achievement system
- Cloud backup for progress
- Voice commands for hands-free control

---

## 📝 License

Free to use and modify for personal/educational purposes.

---

**Made with ♿ accessibility in mind** — For students who learn differently.

*"Your study companion that understands how your brain works."* 🐾

## ✨ Features

### 🎮 Gamification
- **Two Study Modes**:
  - **Default Mode** 📚: Earn rewards just for having the app open (no focus requirement)
  - **Focus Mode** 🎯: Focus detection with sound alerts when you get distracted
- **Leveling**: Level up as you gain XP (XP threshold: level × 100)
- **Shop**: Buy cosmetics like hats with earned currency
- **Secret Code**: Type "posturegod" for +1000 currency bonus
- **Study Sessions**: Track total study time and per-session duration

### ♿ Accessibility Features (Both Modes)
- **Text-to-Speech (T key)**: AI reads screen content aloud with slower speed (150 bpm) for better comprehension
- **Translation Support (L key)**: Translate screen content to Spanish (or any language) using Gemini AI - perfect for ESL learners
- **Simplified Explanations**: All AI prompts emphasize clarity and simplicity
- **ADHD-Friendly**: Context-aware screen analysis simplified for neurodivergent learners

### 🤖 AI Features (via Gemini 2.0 Flash)
- **Screen Analysis (SPACE key)**: AI explains what's on your screen in simple terms
- **Context-Aware Translation**: Gemini understands context for accurate translations
- **Study Material Simplification**: Automatically simplifies complex content

### 🖼️ Pet UI
- **Mode Indicator**: Pet changes color based on mode (Blue 📚 for Default, Red 🎯 for Focus)
- **Bouncing Animation**: Cute bouncing effect while you study
- **Cosmetics**: Equip hats and other cosmetics from the shop
- **Always On Top**: Pet stays visible on top of other windows

## 🚀 Setup

### Prerequisites
- Python 3.9+
- Windows (uses pywin32 for transparent overlay)
- Gemini API key from [aistudio.google.com](https://aistudio.google.com/app/apikeys)

### Installation

1. **Clone/Download this project**
   ```bash
   cd Aether\ Assistant
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Get your Gemini API key from [aistudio.google.com/app/apikeys](https://aistudio.google.com/app/apikeys)
   - Open `.env` and paste your key:
     ```
     GEMINI_API_KEY=your_key_here
     ```

5. **Run the app**
   ```bash
   python main.py
   ```

## 🎮 Controls

| Key | Function |
|-----|----------|
| **F** | Toggle between Default and Focus modes |
| **SPACE** | AI analyzes screen (readable explanation) |
| **T** | Text-to-speech reads the analysis aloud |
| **L** | Translate analysis to Spanish (configurable) |
| **M** | Opens shop dashboard to buy cosmetics |
| Type **"posturegod"** | +1000 currency bonus |
| **ESC** or Close Window | Exit app |

## 📖 Mode Comparison

### Default Mode 📚 (Blue Pet)
- ✅ Earn rewards just by having app open
- ✅ All accessibility features (TTS, translation, AI)
- ✅ Perfect for: ESL learners, ADHD students, breaks from focus
- ❌ No focus detection

### Focus Mode 🎯 (Red Pet)
- ✅ Focus detection with face recognition
- ✅ Sound alerts when you get distracted
- ✅ 3-second grace period for brief interruptions
- ✅ All accessibility features (TTS, translation, AI)
- ✅ Only earn rewards when focused
- ✅ Perfect for: Serious study sessions with accountability

## 🏗️ Project Structure

```
Aether Assistant/
├── main.py              # Game loop & study session tracking
├── pet_brain.py         # AI logic (Gemini + TTS + Translation)
├── pet_ui.py            # Transparent overlay with animations
├── dashboard.py         # Shop & stats interface
├── pet_data.json        # Player progression & study data
├── requirements.txt     # Python dependencies
├── .env.example         # API key template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 📋 File Integration & Mode System

### main.py
- Core game loop that runs at ~30 FPS
- Loads `pet_data.json` each frame (updates currency/XP/level)
- Tracks study session time
- **Mode handling**: Loads mode from pet_data.json and initializes PetBrain accordingly
- **Default Mode**: Continuous rewards + no focus detection
- **Focus Mode**: Focus-based rewards with sound alerts (800 Hz on loss, 600 Hz on regain)
- Detects keyboard input (F = toggle mode, SPACE/T/L = AI features)
- Renders pet via `pet_ui.py`

### pet_brain.py
- **Mode-aware initialization**: Takes `mode` parameter in `__init__`
- **Default Mode**: Skips webcam/face detection initialization
- **Focus Mode**: Initializes MediaPipe face mesh and webcam on demand
- **Conditional imports**: OpenCV and MediaPipe only imported if Focus mode is used
- Generates Gemini responses for screen analysis
- **Text-to-speech** using pyttsx3
- **Translations** using Gemini (context-aware)
- `is_focusing()` returns `True` in Default mode, actual face detection in Focus mode

### pet_ui.py
- Creates transparent pygame window
- **Mode indicator**: Pet color reflects current mode (Blue for Default, Red for Focus)
- Draws pet with bouncing animation
- Uses Windows API (`pywin32`) for transparent overlay
- Shows emoji mode indicator (📚 or 🎯) on pet overlay
- Pet stays on top of other windows

### dashboard.py
- Separate shop interface
- Displays stats (level, currency)
- Allows purchasing hats and cosmetics
- Updates `pet_data.json` when purchases are made

### pet_data.json
- Persistent player data
- Tracks currency, XP, level, equipment
- Includes accessibility settings (language, TTS speed)

## 🔧 How It Works Together

```
Start: main.py
  ↓
Load mode from pet_data.json
  ↓
Create PetBrain(mode=default/focus)
  ├─ Default: Initializes Gemini client + TTS engine only
  └─ Focus: Also initializes MediaPipe face detection + webcam
Create PetUI() → Creates transparent overlay window with animation
  ↓
Main Loop (30 FPS):
  1. Read pet_data.json (load player stats & current mode)
  2. Check is_focusing() based on mode
  3. Award rewards (Default: always | Focus: only when focused)
  4. Sound alerts on focus loss/regain (Focus mode only)
  5. Handle keyboard input:
     - F → Toggle mode (Default ↔ Focus)
     - SPACE → PetBrain.study_the_screen() → Gemini analyzes
     - T → TTS reads analysis aloud
     - L → Translate analysis to Spanish
     - M → Open dashboard
  6. Save updated pet_data.json
  7. Draw pet (color reflects mode)
  8. On exit: Save session time
```

## 🔐 Security

- **API Key**: Stored in `.env` (not in source code)
- **Never commit `.env`**: Added to `.gitignore`
- Use `.env.example` as a template for deployment
- **Webcam (Focus mode only)**: Only activated when explicitly switched to Focus mode

## 🐛 Troubleshooting

### Focus Mode - No webcam detected
- Check if your camera is connected and not in use
- Make sure you've granted camera permissions to Python
- Try: Start in Default mode, then switch to Focus mode (F key)
- Install camera drivers if needed

### Focus Mode - Sound alerts not working
- Check Windows volume is not muted
- Test: `import winsound; winsound.Beep(800, 200)`
- Verify audio drivers are installed

### Gemini API errors
- Verify your API key is valid and has quota remaining
- Check internet connection
- Make sure `.env` file exists and contains the key
- Try running as administrator

### TTS not working
- Windows users: Ensure audio drivers are installed
- Try: `import pyttsx3; engine = pyttsx3.init()` in Python console
- Check system volume is not muted

### Translation not working
- Verify Gemini API key is active
- Check internet connection
- Try analyzing screen content first with SPACE key before translating

### Pet animation is choppy
- Close other applications to free up CPU
- Update your graphics drivers

## 📝 License

Free to use and modify for personal/educational purposes.

## 🤝 Contributing

Feel free to add:
- More pet cosmetics and animations
- Additional languages for translation
- Voice commands for keyboard-free control
- Cloud save system for progress backup
- Pomodoro timer integration
- Study streak tracking
- Rewards/achievement system
- Customizable pet appearance

---

**Made with ♿ accessibility in mind** - For students, ESL learners, and neurodivergent individuals.
