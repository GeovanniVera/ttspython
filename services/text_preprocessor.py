import re

def preprocess(text):
    """
    Cleans and normalizes text for TTS.
    
    Args:
        text (str): Raw text extracted from PDF.
        
    Returns:
        str: Cleaned text.
    """
    if not text:
        return ""
        
    # 1. Join hyphenated words split across lines (e.g. "exam-\nple" -> "example")
    # This is a basic heuristic.
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)
    
    # 2. Replace multiple newlines with a single space or specific pause marker if needed.
    # For now, we want a continuous flow, but keeping paragraphs might be useful.
    # Let's replace single newlines within paragraphs with spaces, but keep double newlines.
    
    # normalize newlines
    text = text.replace('\r\n', '\n')
    
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # 3. Remove likely header/footer artifacts (simple heuristic: single numbers or short patterns)
    # (This is hard to do generically without losing data, so keeping it minimal for now)
    
    return text.strip()
