import faiss
import numpy as np
import json
import os
from pathlib import Path
from typing import List, Dict, Tuple

class FAISSService:
    def __init__(self, index_path: str, metadata_path: str):
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)
        self.index = None
        self.metadata = []
        self.dimension = 384  #
        
    def initialize(self):
        self.index_path.mkdir(parents=True, exist_ok=True)
        index_file = self.index_path / "index.faiss"
        
        if index_file.exists():
            self.index = faiss.read_index(str(index_file))
            print(f" Loaded existing FAISS index with {self.index.ntotal} vectors")
            
            if self.metadata_path.exists():
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                print(f" Loaded {len(self.metadata)} metadata entries")
        else:
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)
            self.index.hnsw.efConstruction = 40
            self.index.hnsw.efSearch = 16
            print(" Created new FAISS HNSW index")
            self.save()
    
    def add_vectors(self, embeddings: np.ndarray, metadata: List[Dict]):
        """Add vectors to the index"""
        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Embedding dimension {embeddings.shape[1]} != {self.dimension}")
        
        self.index.add(embeddings.astype('float32'))
        
        self.metadata.extend(metadata)
        
        self.save()
        print(f" Added {len(embeddings)} vectors to index")
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> Tuple[List[float], List[Dict]]:
        if self.index.ntotal == 0:
            return [], []
        
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        
        results = []
        scores = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1 and idx < len(self.metadata):
                similarity = 1 / (1 + dist)
                scores.append(float(similarity))
                results.append(self.metadata[idx])
        
        return scores, results
    
    def range_search(self, query_embedding: np.ndarray, threshold: float = 0.8) -> Tuple[List[float], List[Dict]]:
        if self.index.ntotal == 0:
            return [], []
        
        distance_threshold = (1 / threshold) - 1
        
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        lims, distances, indices = self.index.range_search(query_embedding, distance_threshold)
        
        results = []
        scores = []
        for dist, idx in zip(distances, indices):
            if idx < len(self.metadata):
                similarity = 1 / (1 + dist)
                scores.append(float(similarity))
                results.append(self.metadata[idx])
        
        return scores, results
    
    def get_count(self) -> int:
        return self.index.ntotal if self.index else 0
    
    def save(self):
        index_file = self.index_path / "index.faiss"
        faiss.write_index(self.index, str(index_file))
        
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def clear(self):
        self.index = faiss.IndexHNSWFlat(self.dimension, 32)
        self.metadata = []
        self.save()
        print(" Cleared FAISS index")

faiss_service = None

def get_faiss_service():
    global faiss_service
    if faiss_service is None:
        index_path = os.getenv("FAISS_INDEX_PATH", "../data/faiss_index")
        metadata_path = os.getenv("METADATA_PATH", "../data/metadata.json")
        faiss_service = FAISSService(index_path, metadata_path)
        faiss_service.initialize()
    return faiss_service