import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class LLMProviderManager:
    """
    Robust LLM provider with automatic fallback support.
    Handles API limits, rate limits, and provider failures gracefully.
    """

    PROVIDER_PRIORITY = ["groq", "gemini", "local"]  # Fallback order

    def __init__(self):
        self.current_provider = "groq"
        self.fallback_mode = False

    def get_llm(self, provider=None, model_name=None, temperature=0.1, max_retries=2):
        """
        Get LLM with automatic fallback support.
        If primary provider fails, automatically tries fallback providers.
        """

        if provider:
            # Explicit provider requested
            return self._get_provider_llm(provider, model_name, temperature)

        # Auto-fallback mode
        for attempt in range(max_retries + 1):
            try:
                provider_to_try = self.PROVIDER_PRIORITY[attempt % len(self.PROVIDER_PRIORITY)]
                logger.info(f"Trying LLM provider: {provider_to_try} (attempt {attempt + 1})")

                llm = self._get_provider_llm(provider_to_try, model_name, temperature)

                # Test the connection with a simple ping
                if self._test_llm_connection(llm):
                    if attempt > 0:
                        logger.warning(f"Successfully switched to fallback provider: {provider_to_try}")
                        self.fallback_mode = True
                    return llm
                else:
                    logger.warning(f"Provider {provider_to_try} connection test failed")
                    continue

            except Exception as e:
                logger.error(f"Provider {provider_to_try} failed: {e}")
                if attempt == max_retries:
                    # All providers failed, return a dummy fallback
                    logger.critical("All LLM providers failed! Using emergency fallback.")
                    return self._get_emergency_fallback()
                continue

    def _get_provider_llm(self, provider, model_name, temperature):
        """Get LLM instance for specific provider"""

        if provider == "groq":
            from langchain_groq import ChatGroq
            api_key = os.getenv("GROQAI_API_KEY")
            if not api_key:
                raise ValueError("GROQAI_API_KEY not found in environment")

            # Use current active model (updated from deprecated llama3-8b-8192)
            default_model = model_name or "llama-3.1-8b-instant"
            return ChatGroq(
                api_key=api_key,
                model_name=default_model,
                temperature=temperature,
                max_tokens=1024,  # Limit token usage
                timeout=30  # Connection timeout
            )

        elif provider == "gemini":
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
            except ImportError:
                raise ValueError("Google Gemini not available. Install with: pip install langchain-google-genai")

            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment")

            default_model = model_name or "gemini-1.5-flash"
            return ChatGoogleGenerativeAI(
                api_key=api_key,
                model=default_model,
                temperature=temperature,
                max_tokens=1024
            )

        elif provider == "local":
            # Local Ollama fallback
            try:
                from langchain_ollama import ChatOllama
            except ImportError:
                try:
                    from langchain_community.chat_models import ChatOllama
                except ImportError:
                    raise ValueError("Local Ollama not available. Install with: pip install langchain-ollama")

            default_model = model_name or "mistral"
            return ChatOllama(
                model=default_model,
                temperature=temperature
            )

        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def _test_llm_connection(self, llm):
        """Test LLM connection with a simple query"""
        try:
            # Simple test to verify API works
            response = llm.invoke("Test connection. Reply with 'OK'.")
            return "OK" in str(response.content).upper()
        except Exception as e:
            logger.error(f"LLM connection test failed: {e}")
            return False

    def _get_emergency_fallback(self):
        """Emergency fallback when all providers fail"""
        from langchain_core.language_models.base import BaseLanguageModel
        from langchain_core.messages import BaseMessage, AIMessage

        class EmergencyFallbackLLM(BaseLanguageModel):
            """Minimal fallback LLM that returns helpful error messages"""

            def _generate(self, messages, **kwargs):
                return AIMessage(content="""I'm sorry, but our AI services are currently experiencing issues. This might be due to high demand or temporary API limits.

Please try again in a few minutes, or contact support if the issue persists.

For immediate assistance, you can:
- Check our knowledge base at etprime.com
- Contact customer support
- Try our basic FAQ section

We apologize for the inconvenience.""")

            @property
            def _llm_type(self):
                return "emergency_fallback"

        return EmergencyFallbackLLM()

# Global instance for easy access
llm_manager = LLMProviderManager()

# Backward compatibility function
def get_llm(provider=None, model_name=None, temperature=0.1):
    """
    Legacy function for backward compatibility.
    Now includes automatic fallback support.
    """
    return llm_manager.get_llm(provider, model_name, temperature)

# Example usage and testing
if __name__ == "__main__":
    print("Testing LLM Provider Manager...")

    # Test primary provider
    try:
        llm = get_llm()
        response = llm.invoke("Say 'System Online' if you can hear me.")
        print(f"LLM says: {response.content}")
    except Exception as e:
        print(f"LLM test failed: {e}")

    # Test fallback simulation (by setting invalid API key temporarily)
    print("\nTesting fallback mechanism...")
    original_key = os.environ.get("GROQAI_API_KEY")
    try:
        os.environ["GROQAI_API_KEY"] = "invalid_key_for_testing"
        llm = get_llm()  # Should fallback to next provider
        response = llm.invoke("Test fallback.")
        print(f"Fallback LLM says: {response.content}")
    except Exception as e:
        print(f"Fallback test: {e}")
    finally:
        if original_key:
            os.environ["GROQAI_API_KEY"] = original_key