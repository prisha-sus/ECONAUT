import io
import json
import asyncio
import subprocess
import tempfile
import os
import numpy as np
import torch
import faster_whisper
from fastapi import WebSocket, WebSocketDisconnect

# ── Lazy load models (only when needed) ───────────────────────────────────────
vad_model = None
vad_utils = None
whisper_model = None
SAMPLE_RATE = 16000

def load_models():
    global vad_model, vad_utils, whisper_model
    if vad_model is None:
        print("[Voice] Loading Silero VAD model...")
        vad_model, vad_utils = torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
            force_reload=False,
            trust_repo=True,
        )
    if whisper_model is None:
        print("[Voice] Loading Faster-Whisper (base) model...")
        whisper_model = faster_whisper.WhisperModel(
            "base",
            device="cpu",
            compute_type="int8",
        )
        print("[Voice] Models loaded.")


def webm_to_float32(webm_bytes: bytes) -> np.ndarray:
    """
    Convert browser webm/opus bytes → float32 numpy array at 16kHz mono.
    Uses ffmpeg subprocess (must be installed on the system).
    """
    # Get the path to ffmpeg in the tools directory
    import os
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ffmpeg_path = os.path.join(script_dir, "tools", "ffmpeg", "ffmpeg-8.1-essentials_build", "bin", "ffmpeg.exe")
    
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
        f.write(webm_bytes)
        tmp_in = f.name

    tmp_out = tmp_in.replace(".webm", ".pcm")

    try:
        subprocess.run([
            ffmpeg_path, "-y",
            "-i", tmp_in,
            "-ar", "16000",      # resample to 16kHz
            "-ac", "1",          # mono
            "-f", "f32le",       # raw float32 little-endian
            tmp_out
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        with open(tmp_out, "rb") as f:
            raw = f.read()

        audio = np.frombuffer(raw, dtype=np.float32).copy()
        print(f"[Audio] Decoded {len(webm_bytes)} webm bytes → {len(audio)} samples ({len(audio)/SAMPLE_RATE:.2f}s)")
        return audio

    finally:
        os.unlink(tmp_in)
        if os.path.exists(tmp_out):
            os.unlink(tmp_out)


def remove_silence_with_vad(audio: np.ndarray) -> np.ndarray:
    """Run Silero VAD and return only voiced segments."""
    load_models()
    (get_speech_timestamps, _, read_audio, *_) = vad_utils
    
    audio_tensor = torch.from_numpy(audio)
    speech_timestamps = get_speech_timestamps(
        audio_tensor,
        vad_model,
        sampling_rate=SAMPLE_RATE,
        threshold=0.30,                 # lowered for better sensitivity
        min_speech_duration_ms=150,
        min_silence_duration_ms=200,
    )

    if not speech_timestamps:
        print("[VAD] No speech found — using full audio anyway")
        return audio  # still try Whisper on full audio

    voiced = [audio[ts["start"]: ts["end"]] for ts in speech_timestamps]
    print(f"[VAD] {len(speech_timestamps)} speech segment(s) kept")
    return np.concatenate(voiced)


def transcribe(audio: np.ndarray) -> str:
    """Run Faster-Whisper on float32 audio array."""
    load_models()
    
    if len(audio) < SAMPLE_RATE * 0.3:   # less than 0.3s — skip
        print("[Whisper] Audio too short, skipping")
        return ""

    segments, info = whisper_model.transcribe(
        audio,
        beam_size=5,
        language="en",
        vad_filter=False,
        word_timestamps=False,
    )
    text = " ".join(seg.text.strip() for seg in segments).strip()
    print(f"[Whisper] ({info.duration:.1f}s) → '{text}'")
    return text


def _process_audio(webm_bytes: bytes) -> str:
    """Full pipeline: webm → float32 → VAD → Whisper. Runs in executor thread."""
    audio = webm_to_float32(webm_bytes)
    audio = remove_silence_with_vad(audio)
    return transcribe(audio)


async def handle_voice_websocket(websocket: WebSocket):
    """
    Voice WebSocket handler.

    Browser → Server:
      Binary frames : webm/opus audio chunks (sent every 250ms by MediaRecorder)
      Text frame    : {"type": "end_of_speech"} — user released mic button

    Server → Browser:
      {"type": "transcript", "text": "..."}
      {"type": "error",      "message": "..."}
      {"type": "ack"}
    """
    await websocket.accept()
    print("[Voice WS] Client connected")

    audio_buffer = bytearray()

    try:
        while True:
            message = await websocket.receive()

            if "bytes" in message and message["bytes"]:
                audio_buffer.extend(message["bytes"])
                await websocket.send_text(json.dumps({"type": "ack"}))

            elif "text" in message and message["text"]:
                data = json.loads(message["text"])

                if data.get("type") == "end_of_speech":
                    if len(audio_buffer) < 1000:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "Audio too short — please hold the button longer"
                        }))
                        audio_buffer.clear()
                        continue

                    print(f"[Voice WS] Processing {len(audio_buffer):,} bytes...")
                    loop = asyncio.get_event_loop()
                    transcript = await loop.run_in_executor(
                        None, _process_audio, bytes(audio_buffer)
                    )
                    await websocket.send_text(json.dumps({
                        "type": "transcript",
                        "text": transcript,
                    }))
                    audio_buffer.clear()

                elif data.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))

    except WebSocketDisconnect:
        print("[Voice WS] Client disconnected")
    except Exception as e:
        print(f"[Voice WS] Error: {e}")
        try:
            await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
        except Exception:
            pass