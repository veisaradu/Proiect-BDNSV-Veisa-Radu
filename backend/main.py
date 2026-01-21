from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from src.routes import search, documents, llm, evaluation

load_dotenv()

app = FastAPI(
    title="Semantic Search API",
    description="Vector database semantic search with FAISS, BM25, hybrid strategies, LLM integration, and evaluation metrics",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(documents.router)
app.include_router(llm.router)
app.include_router(evaluation.router)

@app.get("/")
def read_root():
    return {"message": "Semantic Search API (Groq/Llama3 Edition)", "status": "running"}

@app.get("/api/health")
def health_check():
    from src.services.faiss_service import get_faiss_service
    from src.services.llm_service import get_llm_service
    
    faiss_service = get_faiss_service()
    llm_service = get_llm_service()
    
    return {
        "status": "ok",
        "indexed_vectors": faiss_service.get_count(),
        "llm_available": llm_service.llm is not None
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)