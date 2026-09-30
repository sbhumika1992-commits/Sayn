# SAYN — When Hands Speak, SAYN Gives Them a Voice

> ## SAYN gives a voice to hands through AI

SAYN is an AI-powered accessibility prototype that uses **real-time hand gesture recognition, computer vision, speech recognition, conversational AI, and voice synthesis** to create a hands-free communication interface.

The goal is simple:

**Turn hand gestures into meaningful communication.**

---

## 🌟 Why SAYN?

Communication should not depend on a single method.

SAYN explores how computer vision and AI can allow users to communicate using natural hand movements instead of relying only on conventional typing or speech-based interaction.

A webcam observes the user's hand, the system identifies predefined gestures, and those gestures are converted into actions, letters, words, or voice-based interaction.

---

# ✨ Key Features

### 🤚 Real-Time Hand Tracking

SAYN uses **MediaPipe Hand Landmarker** to detect hand landmarks from a webcam in real time.

The system visualizes the detected hand skeleton while recognizing gestures.

### 🔤 Gesture-to-Letter Communication

SAYN supports gesture-based letter entry.

Current prototype mappings include:

| Gesture | Meaning |
|---|---|
| ✊ Closed fist | Start Letter Mode |
| ✋ Open palm | Stop / Finish Sentence |
| 👍 Thumb gesture | Space |
| ☝️ Index finger | AI Voice |
| Index + Middle | H |
| Index + Middle + Ring | E |
| Thumb + Index | L |
| Thumb + Index + Middle | P |
| 🤏 Thumb + Index pinch | O |

These gestures can be combined to construct words.

### 📝 Real-Time Text Formation

Recognized letters are added to the captured message.

For example:

```text
H → HE → HEL → HELL → HELLO
````

The system prevents the same held gesture from being repeatedly entered while allowing the user to release and repeat a gesture.

### 🎤 AI Voice Interaction

The AI Voice gesture activates a short voice interaction.

The pipeline is:

```text
Voice
  ↓
Browser Microphone
  ↓
Audio Recording
  ↓
Speech-to-Text
  ↓
AI Assistant
  ↓
Voice Response
```

### 🧠 Conversational AI

SAYN can process transcribed user speech through an AI assistant and generate a concise natural-language response.

### 🔊 Voice Output

SAYN supports voice output through the configured text-to-speech service.

A browser speech-synthesis fallback is also available when external voice output is unavailable.

### 📷 Visual Feedback

The interface provides real-time feedback including:

* Camera status
* Detected hand landmarks
* Current gesture
* Letter mode status
* Captured message
* AI response
* Voice status

---

# 🏗️ System Architecture

```text
                   ┌──────────────────┐
                   │      Webcam      │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │ MediaPipe Vision │
                   │  Hand Landmarker │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │ Gesture          │
                   │ Recognition      │
                   └────────┬─────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
        Letter Mode     AI Voice       Controls
              │             │
              ▼             ▼
       Text Formation   Audio Recording
                            │
                            ▼
                     Speech-to-Text
                            │
                            ▼
                     AI Assistant
                            │
                            ▼
                       Text-to-Speech
                            │
                            ▼
                         Speaker
```

---

# 🛠️ Technology Stack

## Frontend

* HTML5
* CSS3
* JavaScript
* WebRTC / MediaDevices API
* MediaRecorder API
* Web Audio API

## Computer Vision

* MediaPipe Tasks Vision
* MediaPipe Hand Landmarker
* Real-time hand landmark detection
* Custom gesture classification

## Backend

* Python
* FastAPI
* Uvicorn
* REST APIs

## AI & Speech

* Groq API
* Whisper speech recognition
* Rime text-to-speech
* Browser Speech Synthesis API as fallback

---

# 📁 Project Structure

```text
SAYN/
│
├── README.md
├── requirements.txt
│
├── backend/
│   └── main.py
│
└── frontend/
    └── SAYN_index_FINAL.html
```

---

# ⚙️ Requirements

Before running SAYN, make sure you have:

* Python 3.10+
* A modern web browser such as Google Chrome
* Working webcam
* Microphone
* Internet connection
* Groq API key
* Rime API key

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd SAYN
```

---

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 API Configuration

Create a `.env` file inside the project root.

```env
GROQ_API_KEY=your_groq_api_key
RIME_API_KEY=your_rime_api_key
```

**Never upload `.env` to GitHub or include it in a public submission.**

For security, API credentials should remain private.

---

# ▶️ Running the Backend

From the project root:

```powershell
python -m uvicorn backend.main:app --reload --port 8000
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

You can verify the backend by opening:

```text
http://127.0.0.1:8000/
```

---

# 🌐 Running the Frontend

Open:

```text
frontend/SAYN_index_FINAL.html
```

in a modern browser.

Allow:

* Camera access
* Microphone access

when prompted.

The frontend communicates with the local FastAPI backend at:

```text
http://127.0.0.1:8000
```

---

# 🎮 How to Use SAYN

## Step 1 — Launch SAYN

Open the frontend and select:

```text
LAUNCH SAYN
```

Allow camera access.

---

## Step 2 — Start Letter Mode

Show a closed fist:

```text
✊
```

SAYN enters **LETTER MODE**.

---

## Step 3 — Enter Letters

Use the supported gestures.

For example:

```text
H → E → L → L → O
```

The captured message becomes:

```text
HELLO
```

---

## Step 4 — Add a Space

Use the configured thumb gesture:

```text
👍
```

This inserts a space between words.

Example:

```text
HELLO WORLD
```

---

## Step 5 — Finish the Sentence

Show:

```text
✋
```

The system exits letter mode and completes the sentence.

---

# 🎤 AI Voice Mode

Show:

```text
☝️
```

to activate AI Voice.

SAYN then:

1. Records the user's voice
2. Sends the audio to the backend
3. Converts speech into text
4. Sends the text to the AI assistant
5. Generates an AI response
6. Converts the response into speech
7. Plays the response

---

# 🧠 Gesture Recognition

The prototype uses hand landmarks rather than image templates.

Each hand contains **21 tracked landmarks**.

The gesture classifier evaluates relationships between these landmarks to determine which fingers are extended and identifies the corresponding gesture.

This makes the prototype lightweight and suitable for real-time interaction.

---

# 🔄 Communication Pipeline

### Gesture Mode

```text
Hand
 ↓
Camera
 ↓
MediaPipe
 ↓
Landmarks
 ↓
Gesture Classifier
 ↓
Letter / Control
 ↓
Captured Text
```

### AI Voice Mode

```text
Hand Gesture
 ↓
AI Voice Activation
 ↓
Microphone
 ↓
Audio Recording
 ↓
Whisper
 ↓
Text
 ↓
Groq AI
 ↓
AI Response
 ↓
Rime TTS
 ↓
Voice
```

---

# 🔒 Privacy & Security

SAYN requires access to the user's:

* Camera
* Microphone

These are required for the core interaction.

API credentials are stored locally through environment variables and should never be exposed publicly.

The project should be configured with private API keys before running AI and voice services.

---

# 🎯 Accessibility Focus

SAYN is designed as an exploration of accessible human-computer interaction.

The project demonstrates how:

**Computer Vision + AI + Voice**

can create alternative communication interfaces.

Rather than requiring every user to adapt to a traditional interface, SAYN explores interfaces that can adapt to different ways of communicating.

---

# 🚀 Future Scope

The current version is a prototype. Future development could include:

* Full sign-language recognition
* Larger gesture vocabulary
* Recognition of complete words
* Two-hand gesture recognition
* Multi-language support
* Personalized gesture training
* Offline AI inference
* On-device processing
* Mobile application
* Wearable-device integration
* Improved gesture robustness under different lighting conditions
* More advanced accessibility controls

---

# 🏆 Project Highlights

### Real-Time

Hand gestures are processed continuously through a webcam.

### Multimodal

SAYN combines:

```text
Vision + Gesture + Text + Voice + AI
```

### Accessible

The interaction is designed around alternative communication methods.

### Extensible

The gesture-recognition architecture can be expanded with additional gestures and languages.

---

# 📌 Current Prototype Limitations

SAYN currently recognizes a predefined set of gestures rather than complete sign language.

Recognition performance can vary depending on:

* Lighting
* Camera quality
* Hand position
* Distance from the camera
* Gesture visibility

The project should therefore be considered an **AI accessibility prototype**, not a complete sign-language translation system.

---

# 👩‍💻 Project Information

**Project:** SAYN
**Category:** AI / Accessibility / Computer Vision
**Focus:** Gesture Recognition & AI-Assisted Communication

### Motto

> **“When hands speak, SAYN gives them a voice.”**

### Short Pitch

> **“SAYN gives a voice to hands through AI.”**

---

# 📜 License

This project is developed as a prototype for educational, research, demonstration, and hackathon purposes.