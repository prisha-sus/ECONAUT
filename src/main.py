import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from .voice_pipeline import handle_voice_websocket

load_dotenv()

app = FastAPI(title="ET AI Concierge - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Phase 3: Serve the audio/ folder so browser can fetch the mp3 ─────────────
# URL: http://localhost:8000/audio/et_daily_commute.mp3
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "audio")
if os.path.isdir(AUDIO_DIR):
    app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")
    print(f"[Audio] Serving static audio from: {os.path.abspath(AUDIO_DIR)}")
else:
    print(f"[Audio] WARNING: audio/ folder not found at {AUDIO_DIR}")


# ── Phase 1: Text WebSocket ────────────────────────────────────────────────────
async def get_agent_response(message: str) -> str:
    """
    MOCK RESPONSE — Replace with:
        from agents.orchestrator import run_agent
        return await run_agent(message)
    """
    await asyncio.sleep(0.8)
    return (
        f"[MOCK] ET Concierge received: '{message}'. "
        "Plug in Member 1's LangGraph agent here."
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected via WebSocket")
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            user_message = data.get("message", "")

            if not user_message.strip():
                continue

            response = await get_agent_response(user_message)
            words = response.split(" ")

            await websocket.send_text(json.dumps({"type": "start"}))
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                await websocket.send_text(json.dumps({
                    "type": "chunk",
                    "content": chunk
                }))
                await asyncio.sleep(0.04)

            await websocket.send_text(json.dumps({"type": "end"}))

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()


# ── Phase 2: Voice WebSocket ───────────────────────────────────────────────────
@app.websocket("/ws/voice")
async def voice_endpoint(websocket: WebSocket):
    await handle_voice_websocket(websocket)


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "ET Concierge WebSocket Backend"}