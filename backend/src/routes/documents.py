from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
from pathlib import Path
import shutil

from src.services.faiss_service import get_faiss_service
from src.services.embedding_service import get_embedding_service
from src.services.keyword_search import get_keyword_service
from src.utils.document_reader import DocumentReader
from src.utils.text_processor import TextProcessor

router = APIRouter(prefix="/api/documents", tags=["documents"])

UPLOAD_DIR = Path(os.getenv("DOCUMENTS_PATH", "../data/documents"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    
    ext = Path(file.filename).suffix.lower()
    if ext not in DocumentReader.SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported: {DocumentReader.SUPPORTED_EXTENSIONS}"
        )
    
    file_path = UPLOAD_DIR / file.filename
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        content = DocumentReader.read_document(file_path)
        content = TextProcessor.clean_text(content)
        chunks = TextProcessor.chunk_text(content, max_chunk_size=500, overlap=50)
        
        metadata_list = []
        for i, chunk in enumerate(chunks):
            metadata = TextProcessor.extract_metadata(
                file.filename,
                chunk_index=i,
                total_chunks=len(chunks)
            )
            metadata['text'] = chunk
            metadata_list.append(metadata)
        
        embedding_service = get_embedding_service()
        embeddings = embedding_service.embed_texts(chunks)
        
        faiss_service = get_faiss_service()
        faiss_service.add_vectors(embeddings, metadata_list)
        
        keyword_service = get_keyword_service()
        keyword_service.index_documents(chunks, metadata_list)
        
        return {
            "message": "Document uploaded and indexed successfully",
            "filename": file.filename,
            "chunks": len(chunks),
            "total_vectors": faiss_service.get_count()
        }
        
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_documents():
    files = list(UPLOAD_DIR.glob("*"))
    
    return {
        "total": len(files),
        "documents": [
            {
                "filename": f.name,
                "size": f.stat().st_size,
                "extension": f.suffix
            }
            for f in files
            if f.is_file()
        ]
    }

@router.delete("/{filename}")
async def delete_document(filename: str):
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    
    file_path.unlink()
    
    return {"message": f"Document {filename} deleted"}

@router.post("/reindex")
async def reindex_all():
    faiss_service = get_faiss_service()
    embedding_service = get_embedding_service()
    keyword_service = get_keyword_service()
    
    faiss_service.clear()
    
    doc_files = DocumentReader.list_documents(UPLOAD_DIR)
    
    all_chunks = []
    all_metadata = []
    
    for doc_file in doc_files:
        content = DocumentReader.read_document(doc_file)
        content = TextProcessor.clean_text(content)
        chunks = TextProcessor.chunk_text(content, max_chunk_size=500, overlap=50)
        
        for i, chunk in enumerate(chunks):
            metadata = TextProcessor.extract_metadata(
                doc_file.name,
                chunk_index=i,
                total_chunks=len(chunks)
            )
            metadata['text'] = chunk
            all_chunks.append(chunk)
            all_metadata.append(metadata)
    
    embeddings = embedding_service.embed_texts(all_chunks)
    
    faiss_service.add_vectors(embeddings, all_metadata)
    keyword_service.index_documents(all_chunks, all_metadata)
    
    return {
        "message": "Reindexing complete",
        "documents": len(doc_files),
        "chunks": len(all_chunks)
    }

@router.get("/stats")
async def get_stats():
    faiss_service = get_faiss_service()
    keyword_service = get_keyword_service()
    
    doc_files = list(UPLOAD_DIR.glob("*"))
    
    return {
        "total_documents": len([f for f in doc_files if f.is_file()]),
        "total_vectors": faiss_service.get_count(),
        "total_keywords": keyword_service.get_count()
    }
