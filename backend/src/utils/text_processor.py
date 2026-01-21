import re
from typing import List, Dict

class TextProcessor:
    @staticmethod
    def clean_text(text: str) -> str:
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def chunk_text(text: str, max_chunk_size: int = 500, overlap: int = 50) -> List[str]:
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                words = current_chunk.split()
                overlap_words = words[-min(overlap, len(words)):]
                current_chunk = ' '.join(overlap_words) + ' ' + sentence
            else:
                current_chunk += ' ' + sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text]
    
    @staticmethod
    def extract_metadata(filename: str, chunk_index: int = 0, total_chunks: int = 1) -> Dict:
        """Extract metadata from filename"""
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        
        return {
            'filename': filename,
            'name': name,
            'extension': ext,
            'chunk_index': chunk_index,
            'total_chunks': total_chunks,
            'source': filename
        }