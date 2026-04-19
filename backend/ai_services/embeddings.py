from sentence_transformers import SentenceTransformer
import numpy as np

try:
    print("🧠 Loading AI Embedding Model (all-MiniLM-L6-v2)...")
    embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    print("✅ AI Embedding Model loaded successfully.")
except Exception as e:
    print(f"⚠️ Warning: Could not load embedding model from Hugging Face: {e}")
    print("ℹ️ Semantic search will be disabled. Falling back to keyword search.")
    embedding_model = None


def get_embedding(text: str) -> np.ndarray:
    """
    Converts input text into an embedding vector.
    Falls back to zero-vector if model is not loaded.
    """
    if embedding_model is None:
        # Return a zero vector of the correct dimension (384 for MiniLM-L6-v2)
        return [0.0] * 384
        
    return embedding_model.encode(text, normalize_embeddings=True).tolist()
