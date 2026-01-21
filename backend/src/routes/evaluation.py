from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict
import numpy as np
import time
import faiss

from src.services.evaluation_service import get_evaluation_service
from src.services.faiss_service import get_faiss_service
from src.services.embedding_service import get_embedding_service
from src.services.keyword_search import get_keyword_service

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])

class BenchmarkRequest(BaseModel):
    queries: List[str]
    k: int = 10
    iterations: int = 10

@router.post("/benchmark")
async def benchmark_search_strategies(request: BenchmarkRequest):
    
    faiss_service = get_faiss_service()
    embedding_service = get_embedding_service()
    keyword_service = get_keyword_service()
    eval_service = get_evaluation_service()
    
    results = {
        "semantic": [],
        "keyword": [],
        "hybrid": []
    }
    
    for query in request.queries:
        query_embedding = embedding_service.embed_text(query)
        
        latencies = []
        for _ in range(request.iterations):
            start = time.time()
            faiss_service.search(query_embedding, k=request.k)
            latencies.append((time.time() - start) * 1000)
        
        results["semantic"].append({
            "query": query,
            "mean_ms": np.mean(latencies),
            "std_ms": np.std(latencies),
            "p95_ms": np.percentile(latencies, 95)
        })
        
        latencies = []
        for _ in range(request.iterations):
            start = time.time()
            keyword_service.search(query, k=request.k)
            latencies.append((time.time() - start) * 1000)
        
        results["keyword"].append({
            "query": query,
            "mean_ms": np.mean(latencies),
            "std_ms": np.std(latencies),
            "p95_ms": np.percentile(latencies, 95)
        })
    
    return results

@router.post("/ann-vs-exact")
async def compare_ann_exact(query: str, k: int = 10):
    
    faiss_service = get_faiss_service()
    embedding_service = get_embedding_service()
    eval_service = get_evaluation_service()
    
    query_embedding = embedding_service.embed_text(query).reshape(1, -1).astype('float32')
    
    dimension = 384
    index_exact = faiss.IndexFlatL2(dimension)
    
    n_total = faiss_service.index.ntotal
    if n_total > 0:
        vectors = np.zeros((n_total, dimension), dtype='float32')
        for i in range(n_total):
            vectors[i] = faiss_service.index.reconstruct(i)
        
        index_exact.add(vectors)
    
    comparison = eval_service.compare_ann_vs_exact(
        query_embedding,
        faiss_service.index,
        index_exact,
        k=k
    )
    
    return {
        "query": query,
        "k": k,
        "total_vectors": n_total,
        **comparison
    }

@router.post("/range-vs-topk")
async def compare_range_topk(query: str, threshold: float = 0.7, k: int = 10):
    
    faiss_service = get_faiss_service()
    embedding_service = get_embedding_service()
    
    query_embedding = embedding_service.embed_text(query)
    
    start = time.time()
    topk_scores, topk_results = faiss_service.search(query_embedding, k=k)
    topk_latency = (time.time() - start) * 1000
    
    start = time.time()
    range_scores, range_results = faiss_service.range_search(query_embedding, threshold=threshold)
    range_latency = (time.time() - start) * 1000
    
    return {
        "query": query,
        "topk": {
            "k": k,
            "results": len(topk_results),
            "latency_ms": topk_latency,
            "min_score": float(min(topk_scores)) if topk_scores else 0.0,
            "max_score": float(max(topk_scores)) if topk_scores else 0.0,
            "avg_score": float(np.mean(topk_scores)) if topk_scores else 0.0
        },
        "range": {
            "threshold": threshold,
            "results": len(range_results),
            "latency_ms": range_latency,
            "min_score": float(min(range_scores)) if range_scores else 0.0,
            "max_score": float(max(range_scores)) if range_scores else 0.0,
            "avg_score": float(np.mean(range_scores)) if range_scores else 0.0
        },
        "analysis": {
            "range_found_more": len(range_results) > len(topk_results),
            "latency_ratio": range_latency / topk_latency if topk_latency > 0 else 0.0,
            "coverage": len(range_results) / max(len(topk_results), 1)
        }
    }

@router.get("/metrics-summary")
async def get_metrics_summary():
    
    faiss_service = get_faiss_service()
    keyword_service = get_keyword_service()
    
    return {
        "index_stats": {
            "total_vectors": faiss_service.get_count(),
            "total_keywords": keyword_service.get_count(),
            "index_type": "IndexHNSWFlat",
            "dimension": 384
        },
        "hnsw_params": {
            "M": 32,
            "efConstruction": 40,
            "efSearch": 16
        },
        "supported_metrics": [
            "Precision@K",
            "Recall@K",
            "F1@K",
            "MAP (Mean Average Precision)",
            "MRR (Mean Reciprocal Rank)",
            "NDCG (Normalized Discounted Cumulative Gain)",
            "Latency (mean, p50, p95, p99)"
        ]
    }
