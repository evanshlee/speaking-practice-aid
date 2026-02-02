# Speaking Practice Aid

<img width="1686" height="1960" alt="image" src="https://github.com/user-attachments/assets/fa07a224-9a6e-4099-b3d5-96b3bb5d1917" />

A local-only web application for analyzing speaking practice recordings. It transcribes speech while preserving fillers (um, uh, like...) and detects pauses, generating a detailed report suitable for AI-assisted feedback.

## Features

- 🎤 **Browser Recording** or **File Upload** (mp3, wav, m4a, webm)
- 🗣️ **Local STT** using faster-whisper (preserves fillers, repetitions)
- ⏸️ **Pause Detection** using Silero VAD (configurable threshold 0.4-1.2s)
- 📋 **Timeline Transcript** with `[PAUSE X.XXXs]` markers
- ⚙️ **Whisper Model Selection** (Tiny, Base, Small)
- 📝 **One-click Copy** for easy sharing

## Prerequisites

1. **Python 3.11** (or 3.12)
   ```bash
   # If using pyenv
   pyenv install 3.11
   pyenv shell 3.11
   ```

2. **Node.js** (18+ recommended)
   ```bash
   brew install node  # or use nvm
   ```

3. **FFmpeg**
   ```bash
   brew install ffmpeg
   ```

## Installation

### 1. Clone and navigate to the project
```bash
git clone https://github.com/evanshlee/speaking-practice.git
cd practice-speaking
```

### 2. Set up the backend
```bash
# Create virtual environment with Python 3.11
python3.11 -m venv venv

# Activate and install dependencies
source venv/bin/activate
pip install -r server/requirements.txt
```

### 3. Set up the frontend
```bash
cd client
npm install
cd ..
```

## Running the Application

### 🔧 First Time Setup & Run

**Fresh clone? No dependencies installed yet?** This one command does it all:
```bash
./setup-and-run.sh
```
This will:
- Create Python virtual environment (if needed)
- Install all backend dependencies
- Install all frontend dependencies  
- Start both backend and frontend servers

**Then open [http://localhost:5173](http://localhost:5173)** in your browser! 🚀

---

### ⚡ Quick Start (Already Set Up)

**Dependencies already installed?** Just run:
```bash
./start.sh
```
This starts both servers instantly.

---

### 🛠️ Manual Start (Advanced)

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
cd server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd client
npm run dev
```

Then open **http://localhost:5173** in your browser.

## Usage

1. Select **Record** or **Upload** mode
2. (Optional) Choose Whisper model size:
   - **Tiny**: Fastest, lower accuracy
   - **Base**: Balanced (recommended)
   - **Small**: Best accuracy, slower
3. (Optional) Adjust pause threshold (0.4-1.2s)
4. Record/upload your speaking sample
5. Click **Transcribe**
6. Wait for processing (varies by audio length and model)
7. Click **Copy** and paste into your preferred AI assistant for feedback

## Report Format

The generated report contains:

- **A) SUMMARY**: Date, duration (speech/silence), word count, WPM
- **B) TIMELINE**: Timestamped transcript with `[PAUSE X.XXXs]` markers

Example:
```
=== A) SUMMARY ===
Date: 2026-01-30
Duration: 62.5s (Speech: 55.2s, Silence: 7.3s)
Words: 142 (Approx. 154 WPM)

=== B) TIMELINE ===
[00:00.000] So, um, I think the main point here is...
[00:05.234] [PAUSE 1.523s]
[00:06.757] And basically, you know, we need to consider...
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ffmpeg not found` | Install with `brew install ffmpeg` |
| Python version errors | Use Python 3.11 or 3.12 with pyenv |
| CORS errors | Ensure backend is running on port 8000 |
| Slow first run | Whisper model downloads on first use (~150MB for base) |
| Port already in use | Kill existing processes or change port |

## Tech Stack

- **Frontend**: Vite + React
- **Backend**: Python FastAPI
- **STT**: faster-whisper (local Whisper implementation)
- **VAD**: Silero VAD

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Local-only processing. No data is sent to external servers.*
