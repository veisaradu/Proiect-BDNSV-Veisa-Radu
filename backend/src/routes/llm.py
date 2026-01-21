from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import time

from src.services.llm_service import get_llm_service
from src.services.faiss_service import get_faiss_service
from src.services.embedding_service import get_embedding_service

router = APIRouter(prefix="/api/llm", tags=["llm"])

class SummarizeRequest(BaseModel):
    texts: List[str]
    max_length: int = 500

class QARequest(BaseModel):
    query: str
    use_retrieval: bool = True
    k: int = 5

class QAResponse(BaseModel):
    answer: str
    confidence: float
    sources_used: int
    retrieval_time_ms: float
    generation_time_ms: float
    context_chunks: List[Dict]

@router.post("/summarize")
async def summarize(request: SummarizeRequest):
    llm_service = get_llm_service()
    
    start_time = time.time()
    summary = llm_service.summarize(request.texts, request.max_length)
    latency = (time.time() - start_time) * 1000
    
    return {
        "summary": summary,
        "sources": len(request.texts),
        "latency_ms": latency
    }

@router.post("/answer", response_model=QAResponse)
async def answer_question(request: QARequest):
    
    retrieval_start = time.time()
    
    if request.use_retrieval:
        faiss_service = get_faiss_service()
        embedding_service = get_embedding_service()
        
        query_embedding = embedding_service.embed_text(request.query)
        scores, results = faiss_service.search(query_embedding, k=request.k)
        
        context = [r['text'] for r in results]
        context_chunks = [
            {
                "text": r['text'],
                "filename": r['filename'],
                "score": float(score)
            }
            for score, r in zip(scores, results)
        ]
    else:
        context = []
        context_chunks = []
    
    retrieval_time = (time.time() - retrieval_start) * 1000
    
    generation_start = time.time()
    llm_service = get_llm_service()
    result = llm_service.answer_question(request.query, context)
    generation_time = (time.time() - generation_start) * 1000
    
    return QAResponse(
        answer=result['answer'],
        confidence=result['confidence'],
        sources_used=result['sources_used'],
        retrieval_time_ms=retrieval_time,
        generation_time_ms=generation_time,
        context_chunks=context_chunks
    )

@router.post("/rag-compare")
async def compare_rag_strategies(query: str, k: int = 5):
    
    from src.services.keyword_search import get_keyword_service
    
    faiss_service = get_faiss_service()
    embedding_service = get_embedding_service()
    keyword_service = get_keyword_service()
    llm_service = get_llm_service()
    
    results = {}
    
    start = time.time()
    query_embedding = embedding_service.embed_text(query)
    scores, docs = faiss_service.search(query_embedding, k=k)
    context = [d['text'] for d in docs]
    answer = llm_service.answer_question(query, context)
    results['semantic_rag'] = {
        **answer,
        'latency_ms': (time.time() - start) * 1000
    }
    
    start = time.time()
    scores, docs = keyword_service.search(query, k=k)
    context = [d['text'] for d in docs]
    answer = llm_service.answer_question(query, context)
    results['keyword_rag'] = {
        **answer,
        'latency_ms': (time.time() - start) * 1000
    }
    
    start = time.time()
    answer = llm_service.answer_question(query, [])
    results['no_retrieval'] = {
        **answer,
        'latency_ms': (time.time() - start) * 1000
    }
    
    return {
        "query": query,
        "comparisons": results
    }
