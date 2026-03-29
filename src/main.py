import os
import sys
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from .agents.router_agent   import router_agent
from .agents.learning_agent import learning_agent
from .agents.beginner_agent import beginner_agent
from .agents.wealth_agent   import wealth_agent
from .agents.news_agent     import news_agent
from .agents.tax_agent      import tax_agent
from .state.agent_state     import AgentState
from .voice_pipeline        import handle_voice_websocket

app = FastAPI(title="ET AI Concierge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "audio")
if os.path.isdir(AUDIO_DIR):
    app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")
    print(f"[Audio] Serving from: {os.path.abspath(AUDIO_DIR)}")
else:
    print(f"[Audio] WARNING: audio/ folder not found at {AUDIO_DIR}")

AGENT_MAP = {
    "learning": learning_agent,
    "wealth":   wealth_agent,
    "news":     news_agent,
    "tax":      tax_agent,
}

# ── Route → human-readable log messages for the transparency panel ─────────────
ROUTE_LOGS = {
    "learning": [
        "🔍 Classifying user intent...",
        "🎓 Routing to Learning Agent...",
        "📚 Querying ET Masterclass catalog...",
        "✅ Response ready.",
    ],
    "wealth": [
        "🔍 Classifying user intent...",
        "💼 Routing to Wealth Agent...",
        "📊 Analysing portfolio context via AA sandbox...",
        "🔎 Scanning FAISS vector store for ET Markets data...",
        "✅ Response ready.",
    ],
    "news": [
        "🔍 Classifying user intent...",
        "📰 Routing to News Agent...",
        "🗃️ Querying FAISS index for latest ET articles...",
        "✅ Response ready.",
    ],
    "tax": [
        "🔍 Classifying user intent...",
        "🧾 Routing to Tax Agent...",
        "📂 Retrieving relevant tax-saving instruments...",
        "✅ Response ready.",
    ],
    "general": [
        "🔍 Classifying user intent...",
        "🤖 Routing to Learning Agent (fallback)...",
        "✅ Response ready.",
    ],
}


async def run_pipeline(user_input: str, websocket: WebSocket) -> dict:
    """
    Full agent pipeline — streams log events to frontend as it runs.
    """
    state: AgentState = {
        "user_input": user_input,
        "persona":    None,
        "intent":     None,
        "route":      "learning",
        "response":   None,
    }

    loop = asyncio.get_event_loop()

    # ── Step 1: Router ─────────────────────────────────────────────────────────
    await websocket.send_text(json.dumps({
        "type": "log",
        "message": "🔍 Classifying user intent..."
    }))

    state = await loop.run_in_executor(None, router_agent, state)
    route   = state.get("route", "learning")
    persona = state.get("persona", "unknown")
    intent  = state.get("intent",  "general")

    print(f"[Router] persona={persona} | intent={intent} | route={route}")

    await websocket.send_text(json.dumps({
        "type":    "log",
        "message": f"🧠 Detected persona: {persona.replace('_', ' ')} | intent: {intent}"
    }))

    # ── Step 2: Route-specific logs ────────────────────────────────────────────
    logs = ROUTE_LOGS.get(route, ROUTE_LOGS["general"])
    # Skip first log (already sent above), skip last (sent after response)
    for log_msg in logs[1:-1]:
        await websocket.send_text(json.dumps({
            "type":    "log",
            "message": log_msg
        }))
        await asyncio.sleep(0.3)   # small delay so logs feel sequential

    # ── Step 3: Specialist agent ───────────────────────────────────────────────
    specialist = AGENT_MAP.get(route, learning_agent)
    state      = await loop.run_in_executor(None, specialist, state)

    await websocket.send_text(json.dumps({
        "type":    "log",
        "message": "✅ Response ready."
    }))

    return {
        "response": state.get("response", "Sorry, I could not generate a response."),
        "persona":  persona,
        "intent":   intent,
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
                result = await run_pipeline(user_message, websocket)
            except Exception as e:
                print(f"[Pipeline Error] {e}")
                await websocket.send_text(json.dumps({
                    "type":    "log",
                    "message": f"❌ Pipeline error: {str(e)}"
                }))
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