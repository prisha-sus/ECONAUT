import json
import os

# Path to your partner offers
OFFERS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'partner_offers.json')

def evaluate_cross_sell_opportunity(user_intent: str) -> str:
    """
    Scans the user's current conversational intent against the trigger keywords
    in the partner offers database. If a match is found, it returns the proactive offer.
    """
    try:
        with open(OFFERS_PATH, 'r') as file:
            offers = json.load(file)
            
        user_intent_lower = user_intent.lower()
        
        for offer in offers:
            # Split the trigger intents into a list (e.g., ["tax saving", "elss", "section 80c"])
            triggers = [t.strip() for t in offer["trigger_intent"].split(',')]
            
            # Check if any of the trigger keywords are in the user's detected intent
            if any(trigger in user_intent_lower for trigger in triggers):
                return offer["details"]
                
        return ""

    except Exception as e:
        return f"Error loading cross-sell database: {str(e)}"

if __name__ == "__main__":
    # Test 1: Should trigger the ET Money offer
    print("Testing Intent: 'How can I do some tax saving this year?'")
    result = evaluate_cross_sell_opportunity("tax saving")
    print("Result:", result if result else "No trigger")
    
    # Test 2: Should trigger the Home Loan offer
    print("\nTesting Intent: 'I am looking at real estate properties.'")
    result = evaluate_cross_sell_opportunity("real estate")
    print("Result:", result if result else "No trigger")
    
    # Test 3: Should not trigger anything
    print("\nTesting Intent: 'What is the stock market doing today?'")
    result = evaluate_cross_sell_opportunity("general market news")
    print("Result:", result if result else "No trigger")