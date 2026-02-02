from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import tempfile
import os

from engine import process_audio_file

app = FastAPI(title="Speaking Practice API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Speaking Practice Backend", "status": "ok"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    source: str = Form("upload"),
    pause_threshold: float = Form(0.6),
    model_size: str = Form("base"),
):
    """
    Transcribe an audio file and generate a detailed report.
    
    - file: Audio file (mp3, wav, m4a, webm, etc.)
    - source: "upload" or "record"
    - pause_threshold: Minimum pause duration in seconds (0.4-1.2)
    - model_size: Whisper model size ("tiny", "base", "small")
    """
    
    # Validate pause threshold
    if not (0.4 <= pause_threshold <= 1.2):
        raise HTTPException(
            status_code=400,
            detail="pause_threshold must be between 0.4 and 1.2 seconds"
        )
    
    # Validate model size
    if model_size not in ("tiny", "base", "small"):
        raise HTTPException(
            status_code=400,
            detail="model_size must be one of: tiny, base, small"
        )
    
    # Save uploaded file to temp location
    suffix = os.path.splitext(file.filename or ".webm")[1]
    fd, temp_path = tempfile.mkstemp(suffix=suffix)
    try:
        os.close(fd)
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # Process the audio
        report = process_audio_file(
            input_path=temp_path,
            source=source,
            pause_threshold_sec=pause_threshold,
            model_size=model_size
        )
        
        return {"report": report}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )
    
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
