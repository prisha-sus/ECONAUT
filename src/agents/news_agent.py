import logging
from src.core.llm_provider import get_llm
from src.tools.rag_engine import load_json_data, build_vector_store
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer
import numpy as np
import os

logger = logging.getLogger(__name__)
llm = get_llm()  # Uses automatic fallback

# Path to FAISS index
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'faiss_index')

class SentenceTransformerEmbeddings:
    """Simple wrapper for sentence-transformers to work with FAISS"""
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        return self.model.encode(texts, convert_to_numpy=True).tolist()

    def embed_query(self, text):
        return self.model.encode([text], convert_to_numpy=True)[0].tolist()

def news_agent(state):
    """
    Handle news and market-related queries with RAG enhancement.
    Falls back gracefully if RAG fails.
    """
    user_text = state["user_input"]

    # Try to load FAISS index for RAG
    relevant_docs = ""
    rag_success = False

    try:
        if os.path.exists(DB_PATH):
            embeddings = SentenceTransformerEmbeddings()
            vector_store = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)
            docs = vector_store.similarity_search(user_text, k=3)
            if docs:
                relevant_docs = "\n\nRelevant information:\n" + "\n".join([f"- {doc.page_content[:300]}..." for doc in docs])
                rag_success = True
                logger.info("RAG search successful")
        else:
            # If no index, try to build it
            logger.info("FAISS index not found, attempting to build...")
            try:
                build_vector_store()
                embeddings = SentenceTransformerEmbeddings()
                vector_store = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)
                docs = vector_store.similarity_search(user_text, k=3)
                if docs:
                    relevant_docs = "\n\nRelevant information:\n" + "\n".join([f"- {doc.page_content[:300]}..." for doc in docs])
                    rag_success = True
                    logger.info("RAG index built and search successful")
            except Exception as build_error:
                logger.warning(f"Could not build FAISS index: {build_error}")
    except Exception as rag_error:
        logger.error(f"RAG search failed: {rag_error}")

    # Prepare prompt with or without RAG context
    if rag_success:
        prompt = f"""You are a financial news expert for ET (Economic Times).

User query: {user_text}

{relevant_docs}

Provide a helpful, accurate response based on the available information. Include specific market data, trends, and insights where relevant. Keep the response concise but informative."""
    else:
        prompt = f"""You are a financial news expert for ET (Economic Times).

User query: {user_text}

Note: Real-time market data is not available right now. Provide general market insights and suggest checking ET's website for latest updates.

Provide a helpful response based on your knowledge of financial markets and current trends."""

    try:
        result = llm.invoke(prompt)
        response = result.content if result.content else "I'm sorry, I couldn't process your news query right now. Please try again later."

        state["response"] = response
        state["route"] = "news"

        logger.info(f"News agent completed successfully (RAG: {rag_success})")

    except Exception as e:
        logger.error(f"News agent LLM call failed: {e}")

        # Emergency fallback response
        state["response"] = """I'm currently experiencing technical difficulties accessing market data.

For the latest market news and updates, please visit:
- ET Prime: https://prime.economictimes.com
- ET Markets: https://economictimes.indiatimes.com/markets

You can also try your query again in a few minutes."""

        state["route"] = "news"

    return state

    prompt = f"""
You are an AI News Concierge for Economic Times.

The user is interested in business news, stock market updates, or financial trends.

Your job:
1. Respond like a premium news assistant
2. Mention ET Prime / premium articles
3. Keep the tone professional and informative
4. Ask one follow-up question
5. Use the relevant information provided to enhance your response

User message:
{user_text}

{relevant_docs}
"""

    response = llm.invoke(prompt)

    state["response"] = response.content
    return state