def chunk_text(text, word_limit=2000):
    """
    Splits text into chunks of approximately 'word_limit' words.
    Tries to split at sentence boundaries if possible (for now, simply by space/word count).
    
    Args:
        text (str): The text to split.
        word_limit (int): Maximum words per chunk.
        
    Returns:
        list: List of text chunks.
    """
    if not text:
        return []
    
    words = text.split()
    chunks = []
    current_chunk = []
    current_count = 0
    
    for word in words:
        current_chunk.append(word)
        current_count += 1
        
        # Check if limit reached
        if current_count >= word_limit:
            # Join and add to chunks
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_count = 0
            
    # Add remaining words
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks
