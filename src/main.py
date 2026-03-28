import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="ET AI Concierge - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Dummy echo handler (swap this out once Member 1's agent is ready) ──────────
async def get_agent_response(message: str) -> str:
    """
    MOCK RESPONSE — Replace this function body with:
        from agents.orchestrator import run_agent
        return await run_agent(message)
    once Member 1's LangGraph agent is wired up.
    """
    await asyncio.sleep(0.8)  # simulate LLM latency
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

            # Simulate streaming by sending the response word-by-word
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


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ET Concierge WebSocket Backend"}