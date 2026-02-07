import os

OUTPUT_DIR = "output"

def prepare_output_structure(pdf_filename):
    """
    Creates the folder structure for a given PDF project.
    Folder structure: output/<BaseName>/chunks/
    
    Args:
        pdf_filename (str): Name of the source PDF.
        
    Returns:
        str: Path to the chunks directory.
    """
    base_name = get_base_name(pdf_filename)
    
    project_dir = os.path.join(OUTPUT_DIR, base_name)
    chunks_dir = os.path.join(project_dir, "chunks")
    
    os.makedirs(chunks_dir, exist_ok=True)
    
    return chunks_dir

def get_base_name(pdf_filename):
    base_name = os.path.splitext(os.path.basename(pdf_filename))[0]
    # Sanitize directory name (basic)
    return "".join([c for c in base_name if c.isalnum() or c in (' ', '-', '_')]).strip()

def get_final_output_dir(pdf_filename):
    """
    Creates/Returns the path to the 'final' output directory.
    output/<BaseName>/final/
    """
    base_name = get_base_name(pdf_filename)
    project_dir = os.path.join(OUTPUT_DIR, base_name)
    final_dir = os.path.join(project_dir, "final")
    
    os.makedirs(final_dir, exist_ok=True)
    return final_dir

def get_chunk_filename(chunks_dir, base_name, index, total):
    """
    Generates the filename for a chunk WAV.
    Format: BaseName_01_of_05.wav (padded based on total)
    """
    # Calculate padding needed
    digits = len(str(total))
    index_str = str(index).zfill(digits)
    
    filename = f"{base_name}_{index_str}.wav"
    return os.path.join(chunks_dir, filename)
