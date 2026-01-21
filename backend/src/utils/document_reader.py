from pathlib import Path
from typing import List
import PyPDF2
from docx import Document as DocxDocument

class DocumentReader:
    SUPPORTED_EXTENSIONS = ['.txt', '.md', '.pdf', '.docx']
    
    @staticmethod
    def read_document(file_path: Path) -> str:
        ext = file_path.suffix.lower()
        
        if ext in ['.txt', '.md']:
            return DocumentReader._read_text(file_path)
        elif ext == '.pdf':
            return DocumentReader._read_pdf(file_path)
        elif ext == '.docx':
            return DocumentReader._read_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    @staticmethod
    def _read_text(file_path: Path) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def _read_pdf(file_path: Path) -> str:
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    
    @staticmethod
    def _read_docx(file_path: Path) -> str:
        doc = DocxDocument(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    
    @staticmethod
    def list_documents(directory: Path) -> List[Path]:
        if not directory.exists():
            return []
        
        documents = []
        for ext in DocumentReader.SUPPORTED_EXTENSIONS:
            documents.extend(directory.glob(f'*{ext}'))
        
        return sorted(documents)