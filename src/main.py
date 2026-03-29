import os
import sys
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

# ── Make sure src/ is on the path so agents can import each other ──────────────
sys.path.insert(0, os.path.dirname(__file__))

# ── Import agents ──────────────────────────────────────────────────────────────
from agents.router_agent   import router_agent
from agents.learning_agent import learning_agent
from agents.beginner_agent import beginner_agent
from agents.wealth_agent   import wealth_agent
from agents.news_agent     import news_agent
from agents.tax_agent      import tax_agent
from state.agent_state     import AgentState

# ── Phase 2: Voice pipeline ────────────────────────────────────────────────────
from voice_pipeline import handle_voice_websocket

app = FastAPI(title="ET AI Concierge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve audio/ folder for TTS jingle (Phase 3) ──────────────────────────────
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "audio")
if os.path.isdir(AUDIO_DIR):
    app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")
    print(f"[Audio] Serving from: {os.path.abspath(AUDIO_DIR)}")

# ── Agent pipeline ─────────────────────────────────────────────────────────────
AGENT_MAP = {
    "learning": learning_agent,
    "wealth":   wealth_agent,
    "news":     news_agent,
    "tax":      tax_agent,
}

async def run_pipeline(user_input: str) -> dict:
    state: AgentState = {
        "user_input": user_input,
        "persona":    None,
        "intent":     None,
        "route":      "learning",
        "response":   None,
    }

    loop = asyncio.get_event_loop()

    # Step 1 — Router
    state = await loop.run_in_executor(None, router_agent, state)
    print(f"[Router] persona={state['persona']} | intent={state['intent']} | route={state['route']}")

    # Step 2 — Specialist agent
    route      = state.get("route", "learning")
    specialist = AGENT_MAP.get(route, learning_agent)
    state      = await loop.run_in_executor(None, specialist, state)

    return {
        "response": state.get("response", "Sorry, I could not generate a response."),
        "persona":  state.get("persona", "unknown"),
        "intent":   state.get("intent",  "general"),
        "route":    route,
    }


# ── Text WebSocket ─────────────────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("[WS] Client connected")
    try:
        while True:
            raw          = await websocket.receive_text()
            data         = json.loads(raw)
            user_message = data.get("message", "").strip()

            if not user_message:
                continue

            await websocket.send_text(json.dumps({"type": "start"}))

            try:
                result = await run_pipeline(user_message)
            except Exception as e:
                print(f"[Pipeline Error] {e}")
                await websocket.send_text(json.dumps({
                    "type":    "chunk",
                    "content": f"Sorry, something went wrong: {str(e)}"
                }))
                await websocket.send_text(json.dumps({"type": "end"}))
                continue

            words = result["response"].split(" ")
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                await websocket.send_text(json.dumps({
                    "type":    "chunk",
                    "content": chunk
                }))
                await asyncio.sleep(0.03)

            await websocket.send_text(json.dumps({
                "type":    "end",
                "persona": result["persona"],
                "intent":  result["intent"],
                "route":   result["route"],
            }))

    except WebSocketDisconnect:
        print("[WS] Client disconnected")
    except Exception as e:
        print(f"[WS Error] {e}")
        try:
            await websocket.close()
        except Exception:
            pass


# ── Voice WebSocket (Phase 2) ──────────────────────────────────────────────────
@app.websocket("/ws/voice")
async def voice_endpoint(websocket: WebSocket):
    await handle_voice_websocket(websocket)


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "ET AI Concierge"}