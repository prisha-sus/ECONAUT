import os
from dotenv import load_dotenv

load_dotenv()

def get_llm(provider="groq", model_name=None, temperature=0.1):
    """
    Factory function to easily switch between LLM providers.
    Usage: llm = get_llm(provider="groq")
    """
    
    if provider == "groq":
        from langchain_groq import ChatGroq
        # Llama 3 70b or 8b are excellent default choices on Groq
        default_model = "openai/gpt-oss-120b" or "llama3-8b-8192" 
        return ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name=default_model,
            temperature=temperature
        )
        
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        default_model = model_name or "gemini-1.5-flash"
        return ChatGoogleGenerativeAI(
            api_key=os.getenv("GOOGLE_API_KEY"),
            model=default_model,
            temperature=temperature
        )
        
    elif provider == "local":
        # Provision for local Ollama fallback if the internet dies
        from langchain_community.chat_models import ChatOllama
        default_model = model_name or "mistral"
        return ChatOllama(
            model=default_model,
            temperature=temperature
        )
        
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

# Example of how Member 1 will use this:
if __name__ == "__main__":
    print("Testing Groq Connection...")
    llm = get_llm(provider="groq")
    response = llm.invoke("Say 'System Online' if you can hear me.")
    print(f"Groq says: {response.content}")