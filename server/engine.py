"""
Audio Processing Engine for Speaking Practice Aid.

Provides audio preprocessing, VAD-based pause detection, 
speech-to-text transcription, and report generation.
"""

import os
import re
import subprocess
import tempfile
import wave
from datetime import datetime
from typing import Optional

from faster_whisper import WhisperModel
from silero_vad import load_silero_vad, get_speech_timestamps, read_audio


def preprocess_audio(input_path: str, output_path: Optional[str] = None) -> str:
    """Convert audio to 16kHz mono WAV using ffmpeg."""
    if output_path is None:
        fd, output_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
    
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ar", "16000",
        "-ac", "1",
        "-acodec", "pcm_s16le",
        output_path,
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")
    return output_path


def detect_pauses(
    wav_path: str,
    pause_threshold_sec: float = 0.6
) -> tuple[list[dict], float, float]:
    """
    Detect speech and pause segments using Silero VAD.
    
    Returns:
        pauses: list of {start, end, duration} dicts
        total_speech_sec: total speech duration
        total_silence_sec: total silence duration
    """
    model = load_silero_vad()
    wav = read_audio(wav_path)
    
    speech_timestamps = get_speech_timestamps(
        wav,
        model,
        sampling_rate=16000,
        min_speech_duration_ms=250,
        min_silence_duration_ms=int(pause_threshold_sec * 1000),
        return_seconds=True
    )
    
    audio_duration = len(wav) / 16000.0
    pauses = []
    total_speech_sec = 0.0
    prev_end = 0.0
    
    for seg in speech_timestamps:
        start = seg['start']
        end = seg['end']
        gap = start - prev_end
        if gap >= pause_threshold_sec:
            pauses.append({
                'start': round(prev_end, 3),
                'end': round(start, 3),
                'duration': round(gap, 3)
            })
        total_speech_sec += (end - start)
        prev_end = end
    
    # Trailing silence
    if prev_end < audio_duration:
        trailing_gap = audio_duration - prev_end
        if trailing_gap >= pause_threshold_sec:
            pauses.append({
                'start': round(prev_end, 3),
                'end': round(audio_duration, 3),
                'duration': round(trailing_gap, 3)
            })
    
    total_silence_sec = sum(p['duration'] for p in pauses)
    return pauses, round(total_speech_sec, 3), round(total_silence_sec, 3)


_whisper_model: Optional[WhisperModel] = None

def get_whisper_model(model_size: str = "base") -> WhisperModel:
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
    return _whisper_model


def transcribe_audio(wav_path: str, model_size: str = "base") -> tuple[str, list[dict]]:
    """
    Transcribe audio using faster-whisper with filler-preserving settings.
    
    Returns:
        transcript: full text
        segments: list of {start, end, text, words} dicts
    """
    model = get_whisper_model(model_size)
    
    filler_prompt = (
        "Um, uh, like, you know, I mean, actually, basically, so, well, "
        "hmm, ah, oh, okay, right, erm. "
        "The speaker may hesitate, repeat words, or use filler words."
    )
    
    segments_gen, _ = model.transcribe(
        wav_path,
        language="en",
        word_timestamps=True,
        condition_on_previous_text=False,
        vad_filter=False,
        initial_prompt=filler_prompt,
        suppress_blank=False,
    )
    
    segments = []
    full_text_parts = []
    
    for seg in segments_gen:
        words = []
        if seg.words:
            for w in seg.words:
                words.append({
                    'word': w.word,
                    'start': round(w.start, 3),
                    'end': round(w.end, 3)
                })
        
        segments.append({
            'start': round(seg.start, 3),
            'end': round(seg.end, 3),
            'text': seg.text.strip(),
            'words': words
        })
        full_text_parts.append(seg.text)
    
    transcript = " ".join(full_text_parts).strip()
    return transcript, segments


def format_timestamp(sec: float) -> str:
    """Format seconds to [MM:SS.mmm]"""
    minutes = int(sec // 60)
    secs = sec % 60
    return f"[{minutes:02d}:{secs:06.3f}]"


def merge_timeline(segments: list[dict], pauses: list[dict]) -> str:
    """
    Merge STT words and pause events into a unified timeline.
    Uses 'Trim and Snap' VAD Bucketing to correctly align words with speech regions.
    """
    # Collect all words
    all_words = []
    for seg in segments:
        if 'words' in seg and seg['words']:
            words_source = seg['words']
        elif seg['text'].strip():
            words_source = [{
                'word': seg['text'],
                'start': seg['start'],
                'end': seg['end']
            }]
        else:
            words_source = []
            
        for w in words_source:
            all_words.append({
                'word': w['word'],
                'start': w['start'],
                'end': w['end'],
                'center': (w['start'] + w['end']) / 2.0
            })

    if not all_words:
        return ""
    
    # Determine max time
    last_word_end = max(w['end'] for w in all_words)
    last_pause_end = max(p['end'] for p in pauses) if pauses else 0
    max_time = max(last_word_end, last_pause_end)
        
    # Build VAD buckets
    buckets = []
    current_time = 0.0
    sorted_pauses = sorted(pauses, key=lambda p: p['start'])
    
    for p in sorted_pauses:
        buckets.append({
            'type': 'speech',
            'start': current_time,
            'end': p['start'],
            'words': []
        })
        buckets.append({
            'type': 'pause',
            'start': p['start'],
            'end': p['end'],
            'duration': p['duration']
        })
        current_time = p['end']
        
    buckets.append({
        'type': 'speech',
        'start': current_time,
        'end': max(max_time, current_time) + 5.0,
        'words': []
    })
    
    def get_corrected_center(w):
        """Trim word timestamps that encroach on pauses."""
        w_start, w_end = w['start'], w['end']
        corrected_start, corrected_end = w_start, w_end
        
        best_p = None
        max_overlap = 0.0
        
        for p in sorted_pauses:
            o_s = max(w_start, p['start'])
            o_e = min(w_end, p['end'])
            if o_e > o_s:
                overlap = o_e - o_s
                if overlap > max_overlap:
                    max_overlap = overlap
                    best_p = p
        
        if best_p:
            right_speech_dur = max(0.0, w_end - best_p['end'])
            if right_speech_dur > 0.01:
                corrected_start = max(corrected_start, best_p['end'])
            else:
                corrected_end = min(corrected_end, best_p['start'])
                
        if corrected_end <= corrected_start:
            return (w_start + w_end) / 2.0
             
        return (corrected_start + corrected_end) / 2.0

    # Assign words to speech buckets
    speech_buckets = [b for b in buckets if b['type'] == 'speech']
    
    for w in all_words:
        center = get_corrected_center(w)
        assigned = False
        
        for b in speech_buckets:
            if b['start'] <= center <= b['end']:
                b['words'].append(w)
                assigned = True
                break
        
        if not assigned:
            min_dist = float('inf')
            best_bucket = None
            for b in speech_buckets:
                if center < b['start']:
                    dist = b['start'] - center
                elif center > b['end']:
                    dist = center - b['end']
                else:
                    dist = 0
                
                if dist < min_dist:
                    min_dist = dist
                    best_bucket = b
            if best_bucket:
                best_bucket['words'].append(w)

    # Render timeline
    render_events = []
    
    for b in buckets:
        if b['type'] == 'speech' and b['words']:
            b['words'].sort(key=lambda x: x['start'])
            
            text_buffer = []
            for w in b['words']:
                t = w['word']
                if not text_buffer:
                    text_buffer.append(t.strip())
                elif not t.startswith(' ') and not re.match(r'^[.,?!]', t):
                    text_buffer.append(" " + t.strip())
                else:
                    text_buffer.append(t)
            
            render_events.append({
                'type': 'speech',
                'raw_time': b['words'][0]['start'],
                'text': "".join(text_buffer).strip()
            })
                
        elif b['type'] == 'pause':
            render_events.append({
                'type': 'pause',
                'raw_time': b['start'],
                'duration': b['duration']
            })
            
    # Build final output with monotonic timestamps
    final_lines = []
    current_cursor = 0.0
    pending_pause = None
    
    for evt in render_events:
        if evt['type'] == 'speech':
            if pending_pause:
                p_start = max(pending_pause['raw_time'], current_cursor)
                final_lines.append(f"{format_timestamp(p_start)} [PAUSE {pending_pause['duration']:.3f}s]")
                current_cursor = p_start
                pending_pause = None
            
            s_start = max(evt['raw_time'], current_cursor)
            current_cursor = s_start 
            final_lines.append(f"{format_timestamp(s_start)} {evt['text']}")
            
        elif evt['type'] == 'pause':
            if pending_pause:
                pending_pause['duration'] += evt['duration']
            else:
                pending_pause = evt
                
    if pending_pause:
        p_start = max(pending_pause['raw_time'], current_cursor)
        final_lines.append(f"{format_timestamp(p_start)} [PAUSE {pending_pause['duration']:.3f}s]")
         
    return "\n".join(final_lines)


def compute_word_count(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def count_fillers(text: str) -> tuple[int, str]:
    """
    Count filler words and return total count and a formatted detail string.
    Targets: um, uh, hm, hmm, er, ah, like, you know, i mean
    """
    fillers = [
        "um", "uh", "hmm", "hm", "er", "ah", 
        "like", "you know", "i mean", "actually", "basically"
    ]
    
    counts = {}
    total = 0
    text_lower = text.lower()
    
    for filler in fillers:
        # Match whole words only
        matches = len(re.findall(fr'\b{re.escape(filler)}\b', text_lower))
        if matches > 0:
            counts[filler] = matches
            total += matches
            
    if total == 0:
        return 0, ""
        
    # Sort by frequency
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    details = ", ".join([f"{k}: {v}" for k, v in sorted_counts])
    
    return total, f"({details})"


def generate_report(
    date: str,
    duration_sec: float,
    transcript_full: str,
    segments: list[dict],
    pauses: list[dict],
    total_speech_sec: float,
    total_silence_sec: float,
) -> str:
    """Generate the final plain-text report."""
    
    # A) Summary
    word_count = compute_word_count(transcript_full)
    speech_minutes = total_speech_sec / 60.0 if total_speech_sec > 0 else 1.0
    wpm = round(word_count / speech_minutes) if speech_minutes > 0 else 0
    
    # Filler count
    filler_count, filler_details = count_fillers(transcript_full)
    
    summary_section = "\n".join([
        "=== A) SUMMARY ===",
        f"Date: {date}",
        f"Duration: {duration_sec:.1f}s (Speech: {total_speech_sec:.1f}s, Silence: {total_silence_sec:.1f}s)",
        f"Words: {word_count} (Approx. {wpm} WPM)",
        f"Fillers: {filler_count} {filler_details}".strip(),
    ])
    
    # B) Timeline
    timeline = merge_timeline(segments, pauses)
    timeline_section = "=== B) TIMELINE ===\n" + timeline
    
    return "\n\n".join([summary_section, timeline_section])


def process_audio_file(
    input_path: str,
    source: str = "upload",
    pause_threshold_sec: float = 0.6,
    model_size: str = "base"
) -> str:
    """
    Full processing pipeline: preprocess -> VAD -> transcribe -> report.
    
    Args:
        input_path: Path to audio file
        source: Source type ("upload" or "record")
        pause_threshold_sec: Minimum pause duration to detect
        model_size: Whisper model size ("tiny", "base", "small")
    
    Returns:
        Report text
    """
    wav_path = preprocess_audio(input_path)
    
    try:
        with wave.open(wav_path, 'rb') as wf:
            duration_sec = wf.getnframes() / float(wf.getframerate())
        
        pauses, total_speech_sec, total_silence_sec = detect_pauses(
            wav_path, pause_threshold_sec
        )
        
        transcript_full, segments = transcribe_audio(wav_path, model_size)
        
        report = generate_report(
            date=datetime.now().strftime("%Y-%m-%d"),
            duration_sec=duration_sec,
            transcript_full=transcript_full,
            segments=segments,
            pauses=pauses,
            total_speech_sec=total_speech_sec,
            total_silence_sec=total_silence_sec
        )
        
        return report
    
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)
