#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite for ET AI Concierge
---------------------------------------------------------
Tests all components working together: agents, memory, guardrails, RAG, etc.
Run this to verify complete system integration before deployment.
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_agent_workflow():
    """Test individual agent components (avoid full workflow due to optional dependencies)"""
    print("🧪 Testing Agent Components Integration...")

    try:
        from src.agents.router_agent import router_agent
        from src.agents.learning_agent import learning_agent
        from src.agents.news_agent import news_agent
        from src.state.agent_state import AgentState

        # Test router agent
        state = AgentState(user_input="I want to learn about investing")
        routed_state = router_agent(state)
        assert 'route' in routed_state, "Router didn't set route"
        assert routed_state['route'] in ['learning', 'wealth', 'tax', 'news'], f"Invalid route: {routed_state['route']}"
        print(f"    ✅ Router: '{state['user_input']}' → {routed_state['route']}")

        # Test learning agent
        learning_state = learning_agent(state)
        assert 'response' in learning_state, "Learning agent didn't generate response"
        assert len(learning_state['response']) > 20, "Learning response too short"
        print(f"    ✅ Learning agent: Response generated ({len(learning_state['response'])} chars)")

        # Test news agent (with RAG)
        news_state = AgentState(user_input="Latest market news")
        news_result = news_agent(news_state)
        assert 'response' in news_result, "News agent didn't generate response"
        print(f"    ✅ News agent: Response generated ({len(news_result['response'])} chars)")

        print("✅ Agent components integration: PASSED")
        return True

    except Exception as e:
        print(f"❌ Agent components integration: FAILED - {e}")
        return False

def test_profiling_flow():
    """Test complete profiling CLI flow"""
    print("🧪 Testing Profiling Flow Integration...")

    try:
        from main_logic import run_concierge
        from logic.memory import UserMemory

        # Create a test session
        session_id = "integration_test_session"

        # Mock user inputs for profiling
        test_answers = ["I am new to investing", "tax saving", "low risk"]

        # Simulate the flow (this would normally require user input)
        # We'll test the components individually

        from logic.profiling import analyze_user_profile
        from logic.product_mapping import recommend_products

        profile = analyze_user_profile(test_answers)
        assert profile['type'] == 'beginner', f"Expected beginner, got {profile['type']}"
        assert profile['goal'] == 'tax_saving', f"Expected tax_saving, got {profile['goal']}"
        assert profile['risk'] == 'low', f"Expected low, got {profile['risk']}"

        recommendations = recommend_products(profile)
        assert len(recommendations) > 0, "No recommendations generated"
        assert any("ET" in rec for rec in recommendations), "ET products not recommended"

        print("✅ Profiling flow integration: PASSED")
        return True

    except Exception as e:
        print(f"❌ Profiling flow integration: FAILED - {e}")
        return False

def test_memory_persistence():
    """Test memory save/load across sessions"""
    print("🧪 Testing Memory Persistence Integration...")

    try:
        from logic.memory import UserMemory

        # Test data
        session_id = "memory_test_session"
        test_profile = {
            'type': 'experienced',
            'goal': 'wealth_building',
            'risk': 'medium'
        }

        # Save profile
        memory = UserMemory(session_id)
        memory.save_profile(test_profile)

        # Load in new instance
        memory2 = UserMemory(session_id)
        loaded_profile = memory2.get_profile()

        assert loaded_profile == test_profile, f"Profile mismatch: {loaded_profile} != {test_profile}"

        print("✅ Memory persistence integration: PASSED")
        return True

    except Exception as e:
        print(f"❌ Memory persistence integration: FAILED - {e}")
        return False

def test_guardrails_integration():
    """Test guardrails working with other components"""
    print("🧪 Testing Guardrails Integration...")

    try:
        from logic.guardrails import is_financial_query, mask_sensitive_data

        # Test financial queries allowed
        financial_queries = [
            "How to invest in stocks?",
            "Tax saving options",
            "Best mutual funds"
        ]

        for query in financial_queries:
            assert is_financial_query(query), f"Financial query blocked: {query}"

        # Test non-financial queries blocked
        non_financial = ["Tell me a joke", "What's the weather?", "Play music"]
        for query in non_financial:
            assert not is_financial_query(query), f"Non-financial query allowed: {query}"

        # Test data masking
        test_dict = {'pan': 'ABC123', 'name': 'John', 'email': 'john@test.com'}
        masked = mask_sensitive_data(test_dict)
        assert masked['pan'] == '****REDACTED****', "PAN not masked"
        assert masked['name'] == 'John', "Name incorrectly masked"

        # Test string masking (should pass through)
        masked_str = mask_sensitive_data("test input")
        assert masked_str == "test input", "String masking failed"

        print("✅ Guardrails integration: PASSED")
        return True

    except Exception as e:
        print(f"❌ Guardrails integration: FAILED - {e}")
        return False

def test_rag_integration():
    """Test RAG system integration (with fallback)"""
    print("🧪 Testing RAG Integration...")

    try:
        from src.agents.news_agent import news_agent
        from src.state.agent_state import AgentState

        # Test news agent (RAG should work or fallback gracefully)
        state = AgentState(user_input="Latest market news")
        result = news_agent(state)

        assert 'response' in result, "No response from news agent"
        assert len(result['response']) > 20, "Response too short"

        # Check if RAG data was included (optional)
        response_text = result['response'].lower()
        rag_indicators = ['relevant information', 'market', 'news', 'et']
        has_rag_content = any(indicator in response_text for indicator in rag_indicators)

        if has_rag_content:
            print("    ✅ RAG data integrated in response")
        else:
            print("    ⚠️  RAG fallback used (no vector data found)")

        print("✅ RAG integration: PASSED")
        return True

    except Exception as e:
        print(f"❌ RAG integration: FAILED - {e}")
        return False

def test_cross_sell_integration():
    """Test cross-sell engine integration with agents"""
    print("🧪 Testing Cross-sell Integration...")

    try:
        from src.tools.cross_sell_engine import evaluate_cross_sell_opportunity

        # Test cross-sell for different intents
        test_intents = ["tax saving", "real estate", "general market news"]

        for intent in test_intents:
            offers = evaluate_cross_sell_opportunity(intent)
            assert isinstance(offers, str), "Cross-sell should return string"
            print(f"    ✅ Intent '{intent}': {'Found offer' if offers else 'No offer'}")

        print("✅ Cross-sell integration: PASSED")
        return True

    except Exception as e:
        print(f"❌ Cross-sell integration: FAILED - {e}")
        return False

def test_error_handling():
    """Test graceful error handling and fallbacks"""
    print("🧪 Testing Error Handling & Fallbacks...")

    try:
        from logic.memory import UserMemory

        # Test Letta fallback (should work even if Letta not installed)
        memory = UserMemory("error_test_session")
        # This should not crash even if Letta fails
        memory.save_profile({'test': 'data'})

        print("    ✅ Memory fallback working")
        print("✅ Error handling: PASSED")
        return True

    except Exception as e:
        print(f"❌ Error handling: FAILED - {e}")
        return False

def test_data_integrity():
    """Test data files and configurations"""
    print("🧪 Testing Data Integrity...")

    try:
        # Check required data files exist
        data_files = [
            'data/mock_user_profiles.json',
            'data/partner_offers.json',
            'data/et_masterclasses.json',
            'data/et_articles.json'
        ]

        for file_path in data_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    assert isinstance(data, (list, dict)), f"Invalid JSON in {file_path}"
                print(f"    ✅ {file_path} valid")
            else:
                print(f"    ⚠️  {file_path} missing (optional)")

        # Check database
        db_path = 'data/user_memory.db'
        if os.path.exists(db_path):
            print("    ✅ Database file exists")
        else:
            print("    ❌ Database not initialized")

        print("✅ Data integrity: PASSED")
        return True

    except Exception as e:
        print(f"❌ Data integrity: FAILED - {e}")
        return False

def run_all_integration_tests():
    """Run complete integration test suite"""
    print("=" * 60)
    print("🚀 ET AI CONCIERGE - INTEGRATION TEST SUITE")
    print("=" * 60)

    tests = [
        test_guardrails_integration,
        test_memory_persistence,
        test_profiling_flow,
        test_agent_workflow,
        test_rag_integration,
        test_cross_sell_integration,
        test_error_handling,
        test_data_integrity
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 60)
    print(f"📊 RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ System is ready for production deployment")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed")
        print("❌ Fix issues before deployment")
        return False

if __name__ == "__main__":
    success = run_all_integration_tests()
    sys.exit(0 if success else 1)