import os
import json
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer
import numpy as np

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'faiss_index')

class SentenceTransformerEmbeddings:
    """Simple wrapper for sentence-transformers to work with FAISS"""
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def embed_documents(self, texts):
        return self.model.encode(texts, convert_to_numpy=True).tolist()
    
    def embed_query(self, text):
        return self.model.encode([text], convert_to_numpy=True)[0].tolist()

def load_json_data(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found.")
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_vector_store():
    print("Initializing Open-Source Vector Database Build...")
    
    masterclasses = load_json_data('et_masterclasses.json')
    articles = load_json_data('et_articles.json')
    
    documents = []
    
    # Process Masterclasses
    for mc in masterclasses:
        content = f"Title: {mc.get('title', '')}\nDescription: {mc.get('description', '')}\nTarget Audience: {mc.get('target_audience', '')}"
        metadata = {"source_type": "masterclass", "id": mc.get('product_id', ''), "url": mc.get('url', '')}
        documents.append(Document(page_content=content, metadata=metadata))
        
    # Process Articles
    for article in articles:
        content = f"Title: {article.get('title', '')}\nSummary: {article.get('description', '')}"
        metadata = {"source_type": "news_article", "category": article.get('category', ''), "url": article.get('url', '')}
        documents.append(Document(page_content=content, metadata=metadata))
        
    print(f"Loaded {len(documents)} total documents.")
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    
    print("Generating embeddings locally via SentenceTransformers... (First run will download the model)")
    # Using a fast, standard open-source embedding model
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2") 
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    vector_store.save_local(DB_PATH)
    print(f"Success! FAISS index saved securely to {DB_PATH}")

if __name__ == "__main__":
    build_vector_store()