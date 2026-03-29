def get_profiling_questions():
    return [
        "Are you new to investing or do you have prior experience?",
        "What is your main financial goal? (Wealth / Tax saving / Home buying / Trading)",
        "What is your risk preference? (Low / Medium / High)"
    ]


def analyze_user_profile(answers):
    profile = {}

    # Safety check
    if len(answers) < 3:
        return {"type": "unknown", "goal": "unknown", "risk": "medium"}

    # Experience
    exp = answers[0].lower()
    if "new" in exp or "beginner" in exp:
        profile["type"] = "beginner"
    else:
        profile["type"] = "experienced"

    # Goal
    goal = answers[1].lower()
    if "tax" in goal:
        profile["goal"] = "tax_saving"
    elif "home" in goal or "house" in goal:
        profile["goal"] = "home_buying"
    elif "trad" in goal:
        profile["goal"] = "trading"
    else:
        profile["goal"] = "investment"

    # Risk
    risk = answers[2].lower()
    if "low" in risk:
        profile["risk"] = "low"
    elif "high" in risk:
        profile["risk"] = "high"
    else:
        profile["risk"] = "medium"

    return profile