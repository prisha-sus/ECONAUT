from src.core.llm_provider import get_llm
from src.tools.rag_engine import load_json_data, build_vector_store
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer
import numpy as np
import os

llm = get_llm(provider="groq")

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
    user_text = state["user_input"]

    # Try to load FAISS index for RAG
    relevant_docs = ""
    try:
        if os.path.exists(DB_PATH):
            embeddings = SentenceTransformerEmbeddings()
            vector_store = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)
            docs = vector_store.similarity_search(user_text, k=3)
            if docs:
                relevant_docs = "\n\nRelevant information:\n" + "\n".join([f"- {doc.page_content[:200]}..." for doc in docs])
        else:
            # If no index, try to build it
            try:
                build_vector_store()
                embeddings = SentenceTransformerEmbeddings()
                vector_store = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)
                docs = vector_store.similarity_search(user_text, k=3)
                if docs:
                    relevant_docs = "\n\nRelevant information:\n" + "\n".join([f"- {doc.page_content[:200]}..." for doc in docs])
            except Exception as e:
                print(f"Could not build/load FAISS index: {e}")
    except Exception as e:
        print(f"RAG search failed: {e}")

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