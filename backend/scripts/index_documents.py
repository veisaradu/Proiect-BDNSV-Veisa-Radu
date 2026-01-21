import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.faiss_service import get_faiss_service
from src.services.embedding_service import get_embedding_service
from src.services.keyword_search import get_keyword_service
from src.utils.document_reader import DocumentReader
from src.utils.text_processor import TextProcessor
from dotenv import load_dotenv
import numpy as np

load_dotenv()

def index_documents(documents_dir: str):
    documents_path = Path(documents_dir)
    
    if not documents_path.exists():
        print(f"Directory not found: {documents_dir}")
        return
    
    print(" Initializing services...")
    faiss_service = get_faiss_service()
    embedding_service = get_embedding_service()
    keyword_service = get_keyword_service()
    
    doc_files = DocumentReader.list_documents(documents_path)
    print(f" Found {len(doc_files)} documents")
    
    if not doc_files:
        print(" No documents found!")
        return
    
    all_chunks = []
    all_metadata = []
    all_texts = []
    
    for doc_file in doc_files:
        print(f"\n Processing: {doc_file.name}")
        
        try:
            content = DocumentReader.read_document(doc_file)
            print(f"   Read {len(content)} characters")
            
            content = TextProcessor.clean_text(content)
            
            chunks = TextProcessor.chunk_text(content, max_chunk_size=500, overlap=50)
            print(f"   Split into {len(chunks)} chunks")
            
            for i, chunk in enumerate(chunks):
                metadata = TextProcessor.extract_metadata(
                    doc_file.name, 
                    chunk_index=i, 
                    total_chunks=len(chunks)
                )
                metadata['text'] = chunk
                
                all_chunks.append(chunk)
                all_metadata.append(metadata)
                all_texts.append(chunk)
            
        except Exception as e:
            print(f"   Error processing {doc_file.name}: {e}")
            continue
    
    if not all_chunks:
        print(" No chunks to index!")
        return
    
    print(f"\n Generating embeddings for {len(all_chunks)} chunks...")
    embeddings = embedding_service.embed_texts(all_chunks)
    print(f" Generated embeddings with shape: {embeddings.shape}")
    
    print("\n Adding to FAISS index...")
    faiss_service.add_vectors(embeddings, all_metadata)
    print(f" FAISS index now contains {faiss_service.get_count()} vectors")
    
    print("\n Indexing for keyword search...")
    keyword_service.index_documents(all_texts, all_metadata)
    print(f" Keyword index contains {keyword_service.get_count()} documents")
    
    print("\n Indexing complete!")

if __name__ == "__main__":
    documents_dir = os.getenv("DOCUMENTS_PATH", "../data/documents")
    
    if len(sys.argv) > 1:
        documents_dir = sys.argv[1]
    
    index_documents(documents_dir)