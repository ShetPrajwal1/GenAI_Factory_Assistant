import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import os
import json
import csv

# We use a lightweight local model to generate embeddings
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
FAISS_INDEX_PATH = 'data/faiss_index.bin'
DOCUMENTS_PATH = 'data/documents.json'

model = SentenceTransformer(EMBEDDING_MODEL_NAME)

def load_documents():
    if os.path.exists(DOCUMENTS_PATH):
        with open(DOCUMENTS_PATH, 'r') as f:
            return json.load(f)
    return []

def save_documents(docs):
    os.makedirs(os.path.dirname(DOCUMENTS_PATH), exist_ok=True)
    with open(DOCUMENTS_PATH, 'w') as f:
        json.dump(docs, f)

def init_faiss(dimension=384):
    """
    Initializes or loads a FAISS index.
    The all-MiniLM-L6-v2 model outputs 384-dimensional vectors.
    """
    if os.path.exists(FAISS_INDEX_PATH):
        print("Loading existing FAISS index...")
        index = faiss.read_index(FAISS_INDEX_PATH)
    else:
        print("Creating new FAISS index...")
        index = faiss.IndexFlatL2(dimension)
    return index

def save_faiss(index):
    os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
    faiss.write_index(index, FAISS_INDEX_PATH)

def ingest_historical_data(csv_path: str):
    """
    Reads a CSV file with columns like 'issue_summary', 'troubleshooting_steps'
    Generates embeddings and adds them to FAISS.
    """
    if not os.path.exists(csv_path):
        print(f"File {csv_path} not found.")
        return

    # To prevent duplicate ingestions if the button is clicked multiple times,
    # we delete the old index and documents if they exist.
    if os.path.exists(FAISS_INDEX_PATH):
        os.remove(FAISS_INDEX_PATH)
    if os.path.exists(DOCUMENTS_PATH):
        os.remove(DOCUMENTS_PATH)

    documents = [] # Start fresh
    index = init_faiss()

    new_docs = []
    texts_to_embed = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Create a rich text representation for embedding
            content = f"Issue: {row.get('issue_summary', '')}\nResolution: {row.get('troubleshooting_steps', '')}"
            texts_to_embed.append(content)
            
            # Store the metadata so we can retrieve it
            doc_id = len(documents) + len(new_docs)
            new_docs.append({
                "id": doc_id,
                "equipment": row.get('equipment_name', 'Unknown'),
                "issue": row.get('issue_summary', ''),
                "resolution": row.get('troubleshooting_steps', '')
            })

    if texts_to_embed:
        embeddings = model.encode(texts_to_embed)
        # FAISS expects float32
        faiss_vectors = np.array(embeddings).astype('float32')
        index.add(faiss_vectors)
        
        save_faiss(index)
        documents.extend(new_docs)
        save_documents(documents)
        print(f"Ingested {len(new_docs)} new records.")

def retrieve_context(query: str, top_k: int = 3) -> str:
    """
    Searches the FAISS index for the closely related issues.
    Returns a formatted string of the relevant context.
    """
    if not os.path.exists(FAISS_INDEX_PATH):
        return "No historical maintenance logs found."

    index = init_faiss()
    documents = load_documents()
    
    if index.ntotal == 0:
        return "No historical maintenance logs found."

    query_embedding = model.encode([query]).astype('float32')
    distances, indices = index.search(query_embedding, top_k)
    
    results = []
    for i, idx in enumerate(indices[0]):
        if idx != -1 and idx < len(documents):
            doc = documents[idx]
            results.append(f"- Past Issue with {doc['equipment']}: {doc['issue']}. Fix used: {doc['resolution']}")
            
    if not results:
        return "No relevant historical issues found."
        
    unique_results = list(set(results))
    return "\n".join(unique_results)
