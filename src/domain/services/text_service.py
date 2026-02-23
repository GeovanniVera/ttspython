import re
from typing import List

class TextService:
    @staticmethod
    def preprocess(text: str) -> str:
        """Cleans and normalizes text for TTS (Restored to simple version)."""
        if not text:
            return ""
        
        # Join hyphenated words
        text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)
        
        # Normalize newlines
        text = text.replace('\r\n', '\n')
        
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    @staticmethod
    def chunk_text(text: str, word_limit: int = 3500) -> List[str]:
        """
        Splits text into simple chunks respecting sentence boundaries.
        Increased limit to 3500 words for better API efficiency.
        """
        if not text:
            return []
        
        # Split by sentence endings (. ! ?), keeping the punctuation
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for sentence in sentences:
            sentence_word_count = len(sentence.split())
            
            if sentence_word_count > word_limit:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_word_count = 0
                
                words = sentence.split()
                for i in range(0, len(words), word_limit):
                    sub_chunk = " ".join(words[i:i + word_limit])
                    chunks.append(sub_chunk)
                continue

            if current_word_count + sentence_word_count > word_limit:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_word_count = sentence_word_count
            else:
                current_chunk.append(sentence)
                current_word_count += sentence_word_count
                
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks
