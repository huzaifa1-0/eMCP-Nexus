from sentence_transformers import SentenceTransformer
import numpy as np

embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def get_embedding(text: str) -> np.ndarray:
    """
    Converts input text into an embedding vector using HuggingFace.
    """
    return embedding_model.encode(text, normalize_embeddings=True).tolist()
