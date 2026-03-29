# """
# ET AI Concierge — Main Orchestration Logic
# ------------------------------------------
# Member 4 Responsibilities (all phases):
#   Phase 1: System prompts + 3-question profiling flow
#   Phase 2: NeMo Guardrails for topical control + Zero-trust data handling
#   Phase 3: Core Memory persistence via Letta (MemGPT) across sessions
#   Phase 4: Polished demo script with complete user journey
# """

# import uuid
# import logging

# from logic.profiling import get_profiling_questions, analyze_user_profile
# from logic.product_mapping import recommend_products
# from logic.guardrails import is_financial_query, get_guardrail_response   # ✅ fixed import
# from logic.guardrails import mask_sensitive_data                           # Zero-Trust
# from logic.memory import UserMemory
# from config.constants import WELCOME_MESSAGE

# logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
# logger = logging.getLogger(__name__)


# def run_concierge(session_id: str = None):
#     """
#     Full ET AI Concierge flow:
#       1. Greet user
#       2. Ask 3 profiling questions (with guardrail check on each answer)
#       3. Analyze profile
#       4. Persist profile via Letta / SQLite memory
#       5. Recommend ET products
#       6. Display Financial Roadmap
#     """

#     # ── Session setup ─────────────────────────────────────────────────────────
#     if not session_id:
#         session_id = str(uuid.uuid4())[:8]

#     memory = UserMemory(session_id=session_id)

#     # ── Welcome ───────────────────────────────────────────────────────────────
#     print("\n" + "=" * 55)
#     print(f"  {WELCOME_MESSAGE}")
#     print("=" * 55)

#     # Check if returning user
#     if memory.has_existing_profile():
#         existing = memory.get_profile()
#         print(f"\n👋 Welcome back! We remembered your profile:")
#         print(f"   Experience : {existing.get('type', 'N/A')}")
#         print(f"   Goal       : {existing.get('goal', 'N/A')}")
#         print(f"   Risk       : {existing.get('risk', 'N/A')}")
#         use_existing = input("\nUse this saved profile? (yes/no): ").strip().lower()
#         if use_existing in ("yes", "y", ""):
#             profile = existing
#             print("\n✅ Using your saved profile.\n")
#             _display_roadmap(profile, memory)
#             return

#     print("\nLet's understand your financial needs in 3 quick questions.\n")

#     # ── 3-Question Profiling Flow ─────────────────────────────────────────────
#     questions = get_profiling_questions()
#     answers = []

#     for i, question in enumerate(questions, 1):
#         print(f"Q{i}: {question}")
#         try:
#             user_input = input("> ").strip()
#         except (EOFError, KeyboardInterrupt):
#             print("\nSession interrupted.")
#             return

#         # Empty input check
#         if not user_input:
#             print("⚠️  Input cannot be empty. Please try again.")
#             return

#         # Guardrail check (NeMo or keyword fallback)
#         if not is_financial_query(user_input):
#             print(f"\n🚫 {get_guardrail_response()}\n")
#             return

#         answers.append(user_input)
#         print()

#     # ── Profile Analysis ──────────────────────────────────────────────────────
#     profile = analyze_user_profile(answers)

#     if not profile or profile.get("type") == "unknown":
#         print("⚠️  Could not analyze your profile properly. Please try again.")
#         return

#     # ── Zero-Trust: mask before any logging ───────────────────────────────────
#     safe_profile = mask_sensitive_data(profile)
#     logger.info(f"Profile analyzed (session {session_id}): {safe_profile}")

#     # ── Persist to Letta / SQLite ─────────────────────────────────────────────
#     memory.save_profile(profile)
#     print("✅ Your profile has been saved for future sessions.\n")

#     # ── Display Roadmap + Recommendations ─────────────────────────────────────
#     _display_roadmap(profile, memory)


# def _display_roadmap(profile: dict, memory: UserMemory):
#     """Display the personalized Financial Roadmap (Phase 4 demo polish)."""

#     recommendations = recommend_products(profile)

#     print("─" * 55)
#     print("  📊 YOUR FINANCIAL PROFILE")
#     print("─" * 55)
#     print(f"  Experience Level  : {profile.get('type', 'N/A').capitalize()}")
#     print(f"  Financial Goal    : {profile.get('goal', 'N/A').replace('_', ' ').capitalize()}")
#     print(f"  Risk Appetite     : {profile.get('risk', 'N/A').capitalize()}")
#     print("─" * 55)

#     print("\n  🗺️  YOUR PERSONALIZED FINANCIAL ROADMAP")
#     print("─" * 55)

#     if recommendations:
#         for idx, rec in enumerate(recommendations, 1):
#             print(f"  {idx}. {rec}")
#     else:
#         print("  No specific recommendations at this time.")

#     print("\n─" * 55)
#     print("  📌 NEXT STEPS")
#     print("─" * 55)
#     goal = profile.get("goal", "investment")
#     risk = profile.get("risk", "medium")

#     next_steps = {
#         "tax_saving":    "→ Start with ELSS funds via ET Money — get 80C benefit up to ₹1.5L",
#         "home_buying":   "→ Check Home Loan eligibility calculators on ET Financial Services",
#         "trading":       "→ Explore ET Markets for live data, F&O tools & expert analysis",
#         "investment":    "→ Begin a ₹500/month SIP on ET Money — small start, big impact",
#     }
#     print(f"  {next_steps.get(goal, '→ Explore ET platform for curated financial content')}")

#     if risk == "low":
#         print("  → Given your low risk appetite, consider Debt Funds or FDs first.")
#     elif risk == "high":
#         print("  → With high risk appetite, Equity & Mid-cap funds may suit you.")

#     print("\n  Visit: https://economictimes.indiatimes.com/\n")
#     print("=" * 55)
#     print("  Thank you for using ET AI Concierge!")
#     print("=" * 55 + "\n")


# if __name__ == "__main__":
#     run_concierge()




"""
ET AI Concierge — Main Orchestration Logic (FINAL INTEGRATED VERSION)
--------------------------------------------------------------------
Member 4 Responsibilities (all phases):
  Phase 1: System prompts + 3-question profiling flow
  Phase 2: NeMo Guardrails for topical control + Zero-trust data handling
  Phase 3: Core Memory persistence via Letta (MemGPT) across sessions
  Phase 4: Polished demo script with complete user journey
"""

import uuid
import logging

from logic.profiling import get_profiling_questions, analyze_user_profile
from logic.product_mapping import recommend_products
from logic.guardrails import (
    is_financial_query,
    get_guardrail_response,
    mask_sensitive_data,
)
from logic.memory import UserMemory
from config.constants import WELCOME_MESSAGE



logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def run_concierge(session_id: str = None):
    """
    Full ET AI Concierge flow:
      1. Welcome user
      2. Check returning user (memory)
      3. 3-question profiling flow (with guardrails)
      4. Profile analysis
      5. Persist memory
      6. Product recommendation
      7. Personalized roadmap
    """

    # ── Session setup ─────────────────────────────────────────────
    if not session_id:
        session_id = str(uuid.uuid4())[:8]

    memory = UserMemory(session_id=session_id)

    print("\n" + "=" * 60)
    print(f"{WELCOME_MESSAGE}")
    print("=" * 60)

    # ── Returning User Flow (Demo Polish) ─────────────────────────
    if memory.has_existing_profile():
        existing = memory.get_profile()

        print("\n👋 Welcome back! We remembered your financial profile:")
        print(f"   Experience : {existing.get('type', 'N/A')}")
        print(f"   Goal       : {existing.get('goal', 'N/A')}")
        print(f"   Risk       : {existing.get('risk', 'N/A')}")

        reuse = input("\nWould you like to reuse this profile? (yes/no): ").strip().lower()

        if reuse in ("yes", "y", ""):
            print("\n✅ Using your saved profile.\n")
            _display_roadmap(existing)
            return
        else:
            print("\nNo problem — let’s update your profile.\n")

    # ── Profiling Flow ────────────────────────────────────────────
    print("I’ll ask you 3 quick questions to personalize your financial roadmap.\n")

    questions = get_profiling_questions()
    answers = []

    for i, question in enumerate(questions, 1):
        while True:
            print(f"Q{i}: {question}")
            user_input = input("> ").strip()

            # Empty input
            if not user_input:
                print("⚠️ Please enter a valid answer.\n")
                continue

            # Guardrails (actual usage inside main flow)
            if not is_financial_query(user_input):
                print(f"\n🚫 {get_guardrail_response()}\n")
                continue

            # Zero-trust masking
            safe_input = mask_sensitive_data(user_input)
            answers.append(safe_input)
            print()
            break

    # ── Profile Analysis ──────────────────────────────────────────
    profile = analyze_user_profile(answers)

    if not profile or profile.get("type") == "unknown":
        print("⚠️ Unable to analyze your profile. Please try again.")
        return

    # Logging (safe)
    logger.info(f"Profile analyzed (session {session_id}): {profile}")

    # ── Save Memory (Phase-3 Requirement) ─────────────────────────
    memory.save_profile(profile)
    print("✅ Your profile has been saved for future sessions.\n")

    # ── Show Final Financial Roadmap ───────────────────────────────
    _display_roadmap(profile)



# ─────────────────────────────────────────────────────────────────
# ROADMAP (Fully Polished Demo Output)
# ─────────────────────────────────────────────────────────────────
def _display_roadmap(profile: dict):
    """Display complete end-to-end financial roadmap"""

    recommendations = recommend_products(profile)

    print("=" * 60)
    print("📊 YOUR FINANCIAL PROFILE")
    print("=" * 60)

    print(f"Experience Level : {profile.get('type', 'N/A').capitalize()}")
    print(f"Financial Goal   : {profile.get('goal', 'N/A').replace('_', ' ').capitalize()}")
    print(f"Risk Appetite    : {profile.get('risk', 'N/A').capitalize()}")

    print("\n" + "=" * 60)
    print("🗺️ YOUR PERSONALIZED FINANCIAL ROADMAP")
    print("=" * 60)

    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    else:
        print("No recommendations found.")

    # ── Smart Next Steps (Demo Polish)
    print("\n" + "=" * 60)
    print("WHAT YOU SHOULD DO NEXT")
    print("=" * 60)

    goal = profile.get("goal", "investment")
    risk = profile.get("risk", "medium")

    if goal == "tax_saving":
        print("→ Start with ELSS mutual funds to save tax under Section 80C.")
    elif goal == "trading":
        print("→ Explore ET Markets for live stock data and trading tools.")
    elif goal == "home_buying":
        print("→ Use ET home-loan calculators to plan your EMI early.")
    else:
        print("→ Start a small SIP (₹500/month) and grow gradually.")

    if risk == "low":
        print("→ Begin with low-risk options like Debt Funds or FDs.")
    elif risk == "high":
        print("→ You can consider Equity or Mid-cap funds.")

    print("\nVisit: https://economictimes.indiatimes.com/")
    print("=" * 60)
    print("Thank you for using ET AI Concierge!")
    print("=" * 60 + "\n")

# ── Run Program ───────────────────────────────────────────────────
if __name__ == "__main__":
    run_concierge()