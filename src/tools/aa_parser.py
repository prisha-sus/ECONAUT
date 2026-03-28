import json
import os

# Define the path to the user profiles
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'mock_user_profiles.json')

def analyze_portfolio_gaps(user_id: str) -> str:
    """
    Simulates parsing data from the Setu/Sahamati Account Aggregator Sandbox.
    Calculates asset allocation and identifies financial gaps.
    """
    try:
        with open(DATA_PATH, 'r') as file:
            profiles = json.load(file)
            
        user_data = next((user for user in profiles if user["user_id"] == user_id), None)
        
        if not user_data or "account_aggregator_data" not in user_data:
            return "Error: No Account Aggregator data found for this user. Please link your bank accounts."
            
        assets = user_data["account_aggregator_data"]["assets"]
        total_wealth = sum(assets.values())
        
        if total_wealth == 0:
            return "User has zero linked assets."

        # Calculate percentages
        savings_pct = (assets.get("savings_account", 0) / total_wealth) * 100
        equity_total = assets.get("mutual_funds", 0) + assets.get("stocks", 0)
        equity_pct = (equity_total / total_wealth) * 100
        
        # Generate Insights for the LLM
        analysis = f"Total Linked Wealth: ₹{total_wealth:,}\n"
        analysis += f"Asset Allocation: {savings_pct:.1f}% in Cash/Savings, {equity_pct:.1f}% in Equity/Mutual Funds.\n"
        
        # Flag gaps for the Cross-Sell Engine
        if savings_pct > 60:
            analysis += "CRITICAL GAP: User has too much idle cash losing to inflation. "
            analysis += "RECOMMENDATION: Trigger cross-sell for ET Money mutual funds or Wealth Creation Masterclass."
        elif equity_pct > 70:
            analysis += "INSIGHT: User is highly invested in equity. "
            analysis += "RECOMMENDATION: Trigger cross-sell for ET Prime Advanced Stock Screeners or Small-Cap Masterclass."
            
        return analysis

    except Exception as e:
        return f"Failed to parse Account Aggregator data: {str(e)}"

if __name__ == "__main__":
    # Quick local test
    print("Testing User 1 (Beginner):")
    print(analyze_portfolio_gaps("u_001"))
    print("\nTesting User 2 (Lapsed Prime):")
    print(analyze_portfolio_gaps("u_002"))