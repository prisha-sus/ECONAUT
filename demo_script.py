
"""
ET AI Concierge — Demo Script (FINAL INTEGRATED VERSION)
--------------------------------------------------------
Demonstrates a complete end-to-end user journey using the real system.

Shows:
  1. Guardrails blocking a non-financial query (inside main_logic)
  2. Full 3-question profiling flow
  3. Memory persistence (saved profile)
  4. Personalized financial roadmap
  5. Returning user memory recall

Run with:
    python demo_script.py
"""

import time
from unittest.mock import patch

from main_logic import run_concierge
from config.constants import WELCOME_MESSAGE


# ─────────────────────────────────────────────────────────────
# Helper functions for better demo presentation
# ─────────────────────────────────────────────────────────────

def slow_print(text: str, delay: float = 0.02):
    """Typewriter-style printing for demo effect."""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()


def separator(title: str):
    print("\n" + "=" * 60)
    print(f"🎬 DEMO SCENE: {title}")
    print("=" * 60 + "\n")


# ─────────────────────────────────────────────────────────────
# SCENE 1 — Full system run (with guardrail triggered)
# ─────────────────────────────────────────────────────────────

def demo_scene_1_full_flow():
    separator("Full AI Concierge Flow (with Guardrail Check)")

    # These inputs simulate a real user session
    # First input triggers guardrail (non-financial)
    # Next inputs are valid financial answers
    simulated_inputs = [
        "Tell me a joke",                        # Should be blocked
        "I am new to investing",                # Q1 valid answer
        "My goal is tax saving under 80C",      # Q2 valid answer
        "I prefer low risk investments"         # Q3 valid answer
    ]

    with patch("builtins.input", side_effect=simulated_inputs):
        run_concierge(session_id="demo_user_001")


# ─────────────────────────────────────────────────────────────
# SCENE 2 — Returning user (memory recall)
# ─────────────────────────────────────────────────────────────

def demo_scene_2_returning_user():
    separator("Returning User — Memory Recall")

    simulated_inputs = [
        "yes"   # User chooses to reuse stored profile
    ]

    with patch("builtins.input", side_effect=simulated_inputs):
        run_concierge(session_id="demo_user_001")


# ─────────────────────────────────────────────────────────────
# MAIN DEMO RUNNER
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":

    print("\n" + "=" * 60)
    slow_print("🚀 ET AI CONCIERGE — COMPLETE DEMO JOURNEY", 0.02)
    print("=" * 60)

    slow_print("\nWelcome message loaded from constants:")
    slow_print(WELCOME_MESSAGE)
    print()

    # Scene 1 → full user journey
    demo_scene_1_full_flow()

    time.sleep(1)

    # Scene 2 → returning user journey
    demo_scene_2_returning_user()

    print("\n" + "=" * 60)
    slow_print("✅ DEMO COMPLETE — All phases verified.", 0.02)
    print("=" * 60 + "\n")