# Speaking Practice Aid

<img width="824" height="720" alt="image" src="https://github.com/user-attachments/assets/fccc9cb3-8486-4a57-b615-ce62d8bdce6f" />


A local-only web application for analyzing speaking practice recordings. It transcribes speech while preserving fillers (um, uh, like...) and detects pauses, generating a detailed report suitable for AI-assisted feedback.

## Features

- 🎤 **Browser Recording** or **File Upload** (mp3, wav, m4a, webm)
- 🗣️ **Local STT** using faster-whisper (preserves fillers, repetitions)
- ⏸️ **Pause Detection** using Silero VAD (configurable threshold 0.4-1.2s)
- 📋 **Timeline Transcript** with `[PAUSE X.XXXs]` markers
- ⚙️ **Whisper Model Selection** (Tiny, Base, Small)
- 📝 **One-click Copy** for easy sharing

## Prerequisites

1. **Python 3.9+** (3.9, 3.10, 3.11, or 3.12)

   <details>
   <summary>macOS / Linux</summary>

   ```bash
   # If using pyenv
   pyenv install 3.11  # or 3.9, 3.10, 3.12
   pyenv shell 3.11
   ```
   </details>

   <details>
   <summary>Windows</summary>

   Download from [python.org](https://www.python.org/downloads/) or:
   ```cmd
   winget install Python.Python.3.11
   ```
   </details>

2. **Node.js** (18+ recommended)

   <details>
   <summary>macOS / Linux</summary>

   ```bash
   brew install node  # or use nvm
   ```
   </details>

   <details>
   <summary>Windows</summary>

   Download from [nodejs.org](https://nodejs.org/) or:
   ```cmd
   winget install OpenJS.NodeJS.LTS
   ```
   </details>

3. **FFmpeg**

   <details>
   <summary>macOS / Linux</summary>

   ```bash
   brew install ffmpeg
   ```
   </details>

   <details>
   <summary>Windows</summary>

   ```cmd
   winget install Gyan.FFmpeg
   ```
   </details>

## Quick Start

> ⚠️ **Prerequisites Required**: Make sure you've installed Python 3.9+, Node.js, and FFmpeg (see [Prerequisites](#prerequisites) above) before running these commands.

### 🔧 First Time Setup & Run

**Fresh clone?** Run this one command after installing prerequisites:

**macOS / Linux:**
```bash
git clone https://github.com/evanshlee/speaking-practice.git
cd speaking-practice
./setup-and-run.sh
```

**Windows (CMD):**
```cmd
git clone https://github.com/evanshlee/speaking-practice.git
cd speaking-practice
setup-and-run.bat
```

This will:
- Create Python virtual environment
- Install all backend dependencies
- Install all frontend dependencies
- Start both backend and frontend servers

**Then open [http://localhost:5173](http://localhost:5173)** in your browser! 🚀

---

### ⚡ Next Time (Already Set Up)

**Dependencies already installed?** Just run:

**macOS / Linux:**
```bash
./start.sh
```

**Windows (CMD):**
```cmd
start.bat
```

This starts both servers instantly.

---

## Manual Installation & Setup (Optional)

If you prefer to install dependencies manually instead of using `setup-and-run.sh`:

### 1. Clone and navigate to the project
```bash
git clone https://github.com/evanshlee/speaking-practice.git
cd practice-speaking
```

### 2. Set up the backend

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r server/requirements.txt
```

**Windows (CMD):**
```cmd
python -m venv venv
call venv\Scripts\activate.bat
pip install -r server\requirements.txt
```

### 3. Set up the frontend
```bash
cd client
npm install
cd ..
```

## Running the Application

After manual installation, you can use `./start.sh` (macOS/Linux) or `start.bat` (Windows) for quick start, or run servers manually:

### 🛠️ Manual Start (Advanced)

**Terminal 1 - Backend (macOS / Linux):**
```bash
source venv/bin/activate
cd server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 1 - Backend (Windows CMD):**
```cmd
call venv\Scripts\activate.bat
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
| `ffmpeg not found` | Install with `brew install ffmpeg` (macOS) or `winget install Gyan.FFmpeg` (Windows) |
| Python version errors | Use Python 3.11 or 3.12 with pyenv (macOS/Linux) or python.org installer (Windows) |
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
