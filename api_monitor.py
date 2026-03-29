#!/usr/bin/env python3
"""
LLM API Health Monitor and Fallback Manager
Monitors API status and provides manual fallback controls.
"""

import os
import logging
import time
from datetime import datetime, timedelta
from src.core.llm_provider import LLMProviderManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIHealthMonitor:
    """Monitor LLM API health and manage fallbacks"""

    def __init__(self):
        self.llm_manager = LLMProviderManager()
        self.last_check = {}
        self.api_limits = {
            "groq": {"daily_limit": 5000, "used_today": 0, "reset_time": None},
            "gemini": {"daily_limit": 1000, "used_today": 0, "reset_time": None},
        }

    def check_api_health(self, provider="groq"):
        """Check if API is healthy and within limits"""
        try:
            # Get API usage from environment or config
            api_key = os.getenv(f"{provider.upper()}_API_KEY")
            if not api_key:
                return {"status": "error", "message": f"API key not configured for {provider}"}

            # Test connection
            llm = self.llm_manager._get_provider_llm(provider, None, 0.1)
            test_result = self.llm_manager._test_llm_connection(llm)

            if test_result:
                return {"status": "healthy", "message": f"{provider} API is working"}
            else:
                return {"status": "error", "message": f"{provider} API test failed"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_fallback_recommendation(self):
        """Recommend best fallback provider based on health checks"""
        providers = ["groq", "gemini", "local"]
        healthy_providers = []

        for provider in providers:
            health = self.check_api_health(provider)
            if health["status"] == "healthy":
                healthy_providers.append(provider)

        if not healthy_providers:
            return "emergency_fallback"

        # Prefer Groq, then Gemini, then local
        priority_order = ["groq", "gemini", "local"]
        for provider in priority_order:
            if provider in healthy_providers:
                return provider

        return healthy_providers[0]

    def force_fallback(self, provider):
        """Manually force a specific provider"""
        try:
            llm = self.llm_manager.get_llm(provider=provider)
            test_result = self.llm_manager._test_llm_connection(llm)

            if test_result:
                logger.info(f"Successfully switched to {provider}")
                return {"status": "success", "provider": provider}
            else:
                return {"status": "error", "message": f"{provider} test failed"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

def main():
    """CLI interface for API health monitoring"""
    monitor = APIHealthMonitor()

    print("🔍 LLM API Health Monitor")
    print("=" * 40)

    # Check all providers
    providers = ["groq", "gemini", "local"]
    for provider in providers:
        print(f"\n📊 Checking {provider.upper()}...")
        health = monitor.check_api_health(provider)
        status_icon = "✅" if health["status"] == "healthy" else "❌"
        print(f"   {status_icon} {health['message']}")

    # Get recommendation
    print("\n🎯 Recommended Provider:")
    recommendation = monitor.get_fallback_recommendation()
    print(f"   {recommendation.upper()}")

    # Test fallback
    print("\n🔄 Testing Fallback System...")
    try:
        llm = monitor.llm_manager.get_llm()
        response = llm.invoke("Hello, system check.")
        print(f"   ✅ Fallback system working: {response.content[:50]}...")
    except Exception as e:
        print(f"   ❌ Fallback system failed: {e}")

    print("\n💡 Commands:")
    print("   python api_monitor.py check <provider>  # Check specific provider")
    print("   python api_monitor.py switch <provider>  # Force switch to provider")
    print("   python api_monitor.py status             # Show current status")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        monitor = APIHealthMonitor()
        command = sys.argv[1]

        if command == "check" and len(sys.argv) > 2:
            provider = sys.argv[2]
            health = monitor.check_api_health(provider)
            print(f"{provider.upper()}: {health['status']} - {health['message']}")

        elif command == "switch" and len(sys.argv) > 2:
            provider = sys.argv[2]
            result = monitor.force_fallback(provider)
            print(f"Switch to {provider}: {result}")

        elif command == "status":
            main()

        else:
            print("Usage: python api_monitor.py [check <provider>|switch <provider>|status]")
    else:
        main()