from pypdf import PdfReader
import os

def extract_text(filepath):
    """
    Extracts text from a PDF file.
    
    Args:
        filepath (str): Path to the PDF file.
        
    Returns:
        tuple: (full_text, metadata)
            full_text (str): The concatenated text from all pages.
            metadata (dict): Info about the extraction (num_pages, success).
            
    Raises:
        Exception: If file read fails.
    """
    if not os.path.exists(filepath):
        return None, {"error": "File not found"}

    try:
        reader = PdfReader(filepath)
        text_content = []
        num_pages = len(reader.pages)
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_content.append(text)
        
        full_text = "\n".join(text_content)
        
        metadata = {
            "num_pages": num_pages,
            "success": True,
            "char_count": len(full_text)
        }
        
        return full_text, metadata
        
    except Exception as e:
        return None, {"error": str(e), "success": False}
