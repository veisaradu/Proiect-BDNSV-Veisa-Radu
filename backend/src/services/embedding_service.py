from sentence_transformers import SentenceTransformer
import numpy as np
import os

class EmbeddingService:
    def __init__(self, model_name: str = None):
        if model_name is None:
            model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print(f" Embedding model loaded (dimension: {self.model.get_sentence_embedding_dimension()})")
    
    def embed_text(self, text: str) -> np.ndarray:
        return self.model.encode(text, convert_to_numpy=True)
    
    def embed_texts(self, texts: list) -> np.ndarray:
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)

embedding_service = None

def get_embedding_service():
    global embedding_service
    if embedding_service is None:
        embedding_service = EmbeddingService()
    return embedding_service