import subprocess
import os

def check_ffmpeg():
    """
    Checks if FFmpeg is installed and accessible in the system PATH.
    Returns True if available, False otherwise.
    """
    try:
        # Run 'ffmpeg -version' to check availablity
        subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL, 
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def validate_pdf(filepath):
    """
    Validates if a file is a valid PDF.
    Checks:
    1. File existence
    2. .pdf extension
    3. Magic number (%PDF)
    
    Returns (True, "Valid") or (False, "Error message")
    """
    if not os.path.exists(filepath):
        return False, "El archivo no existe."
        
    if not filepath.lower().endswith('.pdf'):
        return False, "El archivo no tiene extensión .pdf"
        
    try:
        with open(filepath, 'rb') as f:
            header = f.read(5)
            if header != b'%PDF-':
                return False, "El archivo no es un PDF válido (cabecera incorrecta)."
    except Exception as e:
        return False, f"Error al leer el archivo: {str(e)}"
        
    return True, "PDF válido."
