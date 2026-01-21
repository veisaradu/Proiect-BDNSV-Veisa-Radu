import time
import numpy as np
from typing import List, Dict, Tuple
from collections import defaultdict

class EvaluationService:
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def calculate_precision_at_k(self, retrieved: List[int], relevant: List[int], k: int) -> float:
        retrieved_k = retrieved[:k]
        relevant_retrieved = len(set(retrieved_k) & set(relevant))
        return relevant_retrieved / k if k > 0 else 0.0
    
    def calculate_recall_at_k(self, retrieved: List[int], relevant: List[int], k: int) -> float:
        retrieved_k = retrieved[:k]
        relevant_retrieved = len(set(retrieved_k) & set(relevant))
        return relevant_retrieved / len(relevant) if relevant else 0.0
    
    def calculate_f1_at_k(self, precision: float, recall: float) -> float:
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    def calculate_map(self, retrieved_lists: List[List[int]], relevant_lists: List[List[int]]) -> float:
        aps = []
        
        for retrieved, relevant in zip(retrieved_lists, relevant_lists):
            if not relevant:
                continue
            
            ap = 0.0
            relevant_count = 0
            
            for i, doc_id in enumerate(retrieved):
                if doc_id in relevant:
                    relevant_count += 1
                    precision_at_i = relevant_count / (i + 1)
                    ap += precision_at_i
            
            ap /= len(relevant)
            aps.append(ap)
        
        return np.mean(aps) if aps else 0.0
    
    def calculate_ndcg(self, retrieved: List[int], relevant: Dict[int, float], k: int) -> float:
        dcg = 0.0
        for i, doc_id in enumerate(retrieved[:k]):
            rel = relevant.get(doc_id, 0.0)
            dcg += (2 ** rel - 1) / np.log2(i + 2)
        
        ideal_scores = sorted(relevant.values(), reverse=True)[:k]
        idcg = sum((2 ** rel - 1) / np.log2(i + 2) for i, rel in enumerate(ideal_scores))
        
        return dcg / idcg if idcg > 0 else 0.0
    
    def calculate_mrr(self, retrieved_lists: List[List[int]], relevant_lists: List[List[int]]) -> float:
        rrs = []
        
        for retrieved, relevant in zip(retrieved_lists, relevant_lists):
            for i, doc_id in enumerate(retrieved):
                if doc_id in relevant:
                    rrs.append(1 / (i + 1))
                    break
            else:
                rrs.append(0.0)
        
        return np.mean(rrs) if rrs else 0.0
    
    def benchmark_latency(self, search_func, query, iterations: int = 10) -> Dict:
        latencies = []
        
        for _ in range(iterations):
            start = time.time()
            _ = search_func(query)
            latency = (time.time() - start) * 1000
            latencies.append(latency)
        
        return {
            "mean_ms": np.mean(latencies),
            "std_ms": np.std(latencies),
            "min_ms": np.min(latencies),
            "max_ms": np.max(latencies),
            "p50_ms": np.percentile(latencies, 50),
            "p95_ms": np.percentile(latencies, 95),
            "p99_ms": np.percentile(latencies, 99)
        }
    
    def compare_ann_vs_exact(self, query_embedding, index_ann, index_exact, k: int = 10) -> Dict:
        start = time.time()
        distances_ann, indices_ann = index_ann.search(query_embedding, k)
        latency_ann = (time.time() - start) * 1000
        
        start = time.time()
        distances_exact, indices_exact = index_exact.search(query_embedding, k)
        latency_exact = (time.time() - start) * 1000
        
        recall = len(set(indices_ann[0]) & set(indices_exact[0])) / k
        
        return {
            "ann_latency_ms": latency_ann,
            "exact_latency_ms": latency_exact,
            "speedup": latency_exact / latency_ann,
            "recall": recall,
            "ann_indices": indices_ann[0].tolist(),
            "exact_indices": indices_exact[0].tolist()
        }

evaluation_service = EvaluationService()

def get_evaluation_service():
    return evaluation_service
