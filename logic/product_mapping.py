def recommend_products(profile):
    recommendations = []

    user_type = profile.get("type", "")
    goal = profile.get("goal", "")

    # Beginner
    if user_type == "beginner":
        recommendations.append("ET Masterclass: Stock Market Basics")
        recommendations.append("ET Prime: Beginner Investment Articles")

    # Goals
    if goal == "tax_saving":
        recommendations.append("ET Money: Tax Saving Tools (ELSS, 80C)")
    elif goal == "home_buying":
        recommendations.append("ET Financial Services: Home Loan Assistance")
    elif goal == "trading":
        recommendations.append("ET Markets: Advanced Trading Tools")
    elif goal == "investment":
        recommendations.append("ET Prime: Wealth Building Guides")

    # Remove duplicates & limit to 3
    final_recommendations = list(dict.fromkeys(recommendations))
    return final_recommendations[:3]