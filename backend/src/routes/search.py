from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import time

from src.services.faiss_service import get_faiss_service
from src.services.embedding_service import get_embedding_service
from src.services.keyword_search import get_keyword_service

router = APIRouter(prefix="/api/search", tags=["search"])

class SearchRequest(BaseModel):
    query: str
    k: int = 5
    strategy: str = "semantic"  
class SearchResult(BaseModel):
    score: float
    text: str
    filename: str
    chunk_index: int
    total_chunks: int
    source: str

class SearchResponse(BaseModel):
    query: str
    strategy: str
    results: List[SearchResult]
    latency_ms: float
    total_results: int

@router.post("/", response_model=SearchResponse)
async def search(request: SearchRequest):
    start_time = time.time()
    
    faiss_service = get_faiss_service()
    embedding_service = get_embedding_service()
    keyword_service = get_keyword_service()
    
    try:
        if request.strategy == "semantic":
            query_embedding = embedding_service.embed_text(request.query)
            scores, results = faiss_service.search(query_embedding, k=request.k)
            
        elif request.strategy == "keyword":
            scores, results = keyword_service.search(request.query, k=request.k)
            
        elif request.strategy == "hybrid":
            query_embedding = embedding_service.embed_text(request.query)
            
            sem_scores, sem_results = faiss_service.search(query_embedding, k=request.k * 2)
            
            kw_scores, kw_results = keyword_service.search(request.query, k=request.k * 2)
            
            combined = {}
            
            for score, result in zip(sem_scores, sem_results):
                key = f"{result['filename']}_{result['chunk_index']}"
                combined[key] = {
                    'result': result,
                    'sem_score': score,
                    'kw_score': 0.0
                }
            
            for score, result in zip(kw_scores, kw_results):
                key = f"{result['filename']}_{result['chunk_index']}"
                if key in combined:
                    combined[key]['kw_score'] = score
                else:
                    combined[key] = {
                        'result': result,
                        'sem_score': 0.0,
                        'kw_score': score
                    }
            
            hybrid_results = []
            for item in combined.values():
                hybrid_score = 0.7 * item['sem_score'] + 0.3 * item['kw_score']
                hybrid_results.append((hybrid_score, item['result']))
            
            hybrid_results.sort(reverse=True, key=lambda x: x[0])
            
            scores = [score for score, _ in hybrid_results[:request.k]]
            results = [result for _, result in hybrid_results[:request.k]]
            
        elif request.strategy == "range":
            query_embedding = embedding_service.embed_text(request.query)
            scores, results = faiss_service.range_search(query_embedding, threshold=0.7)
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown strategy: {request.strategy}")
        
        latency_ms = (time.time() - start_time) * 1000
        
        formatted_results = [
            SearchResult(
                score=score,
                text=result['text'],
                filename=result['filename'],
                chunk_index=result['chunk_index'],
                total_chunks=result['total_chunks'],
                source=result['source']
            )
            for score, result in zip(scores, results)
        ]
        
        return SearchResponse(
            query=request.query,
            strategy=request.strategy,
            results=formatted_results,
            latency_ms=latency_ms,
            total_results=len(formatted_results)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare")
async def compare_strategies(query: str, k: int = 5):
    strategies = ["semantic", "keyword", "hybrid", "range"]
    
    comparisons = {}
    
    for strategy in strategies:
        request = SearchRequest(query=query, k=k, strategy=strategy)
        result = await search(request)
        comparisons[strategy] = result
    
    return {
        "query": query,
        "comparisons": comparisons
    }
