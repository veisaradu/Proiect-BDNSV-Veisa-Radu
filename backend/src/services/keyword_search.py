from rank_bm25 import BM25Okapi
from typing import List, Dict, Tuple

class KeywordSearchService:
    def __init__(self):
        self.bm25 = None
        self.documents = []
        self.metadata = []
    
    def index_documents(self, documents: List[str], metadata: List[Dict]):
        self.documents = documents
        self.metadata = metadata
        
        tokenized_docs = [doc.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)
        
        print(f" Indexed {len(documents)} documents for keyword search")
    
    def search(self, query: str, k: int = 5) -> Tuple[List[float], List[Dict]]:
        if self.bm25 is None or len(self.documents) == 0:
            return [], []
        
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        
        top_k_indices = scores.argsort()[-k:][::-1]
        
        results = []
        result_scores = []
        for idx in top_k_indices:
            if scores[idx] > 0:  
                result_scores.append(float(scores[idx]))
                results.append(self.metadata[idx])
        
        return result_scores, results
    
    def get_count(self) -> int:
        return len(self.documents)

keyword_service = None

def get_keyword_service():
    global keyword_service
    if keyword_service is None:
        keyword_service = KeywordSearchService()
    return keyword_service