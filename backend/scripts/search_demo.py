import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.faiss_service import get_faiss_service
from src.services.embedding_service import get_embedding_service
from src.services.keyword_search import get_keyword_service
from dotenv import load_dotenv

load_dotenv()

def search_demo(query: str, k: int = 5):
    print(f"\n Query: '{query}'")
    print("=" * 60)
    
    faiss_service = get_faiss_service()
    embedding_service = get_embedding_service()
    keyword_service = get_keyword_service()
    
    query_embedding = embedding_service.embed_text(query)
    
    print("\n Semantic Search (FAISS):")
    print("-" * 60)
    scores, results = faiss_service.search(query_embedding, k=k)
    
    if results:
        for i, (score, result) in enumerate(zip(scores, results), 1):
            print(f"\n{i}. Score: {score:.4f}")
            print(f"   Source: {result['filename']} (chunk {result['chunk_index'] + 1}/{result['total_chunks']})")
            print(f"   Text: {result['text'][:150]}...")
    else:
        print("No results found")
    
    print("\n\n Keyword Search (BM25):")
    print("-" * 60)
    scores, results = keyword_service.search(query, k=k)
    
    if results:
        for i, (score, result) in enumerate(zip(scores, results), 1):
            print(f"\n{i}. Score: {score:.4f}")
            print(f"   Source: {result['filename']} (chunk {result['chunk_index'] + 1}/{result['total_chunks']})")
            print(f"   Text: {result['text'][:150]}...")
    else:
        print("No results found")
    
    print("\n\n Range Search (similarity > 0.8):")
    print("-" * 60)
    scores, results = faiss_service.range_search(query_embedding, threshold=0.8)
    
    print(f"Found {len(results)} results within range")
    if results:
        for i, (score, result) in enumerate(zip(scores, results[:3]), 1):  
            print(f"\n{i}. Score: {score:.4f}")
            print(f"   Source: {result['filename']}")
            print(f"   Text: {result['text'][:100]}...")

if __name__ == "__main__":
    query = "What is machine learning?"
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    
    search_demo(query)