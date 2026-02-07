import subprocess
import os
from glob import glob

def merge_wavs(base_dir, base_name, total_chunks):
    """
    Merges all WAV files in the chunks directory into a single WAVFile.
    
    Args:
        base_dir (str): output/<BaseName>/chunks/
        base_name (str): Cleaned project name
        total_chunks (int): Expected number of chunks.
        
    Returns:
        str: Path to the final merged WAV.
        
    Raises:
        Exception: If FFmpeg fails or too many chunks are missing.
    """
    
    # 1. Identify chunks
    # We expect files based on our naming convention: BaseName_01.wav
    # Globs are unpredictable in order, so we reconstruct filenames to be sure of order.
    
    chunks = []
    missing_count = 0
    
    if not os.path.exists(base_dir):
         raise Exception(f"Directory not found: {base_dir}")
         
    # Reconstruct expected filenames to ensure order
    # Needs to match output_manager logic. Digits padding.
    digits = len(str(total_chunks))
    
    for i in range(1, total_chunks + 1):
        index_str = str(i).zfill(digits)
        # Match naming convention from output_manager: f"{base_name}_{index_str}.wav"
        # Wait, output_manager.get_chunk_filename uses:
        # filename = f"{base_name}_{index_str}.wav"
        filename = os.path.join(base_dir, f"{base_name}_{index_str}.wav")
        
        if os.path.exists(filename):
            chunks.append(filename)
        else:
            missing_count += 1
            print(f"Warning: Chunk missing: {filename}")

    # 2. Validation
    if total_chunks > 0:
        missing_pct = missing_count / total_chunks
        if missing_pct > 0.05: # > 5% missing
             raise Exception(f"Too many missing chunks ({missing_count}/{total_chunks}). Aborting merge.")
    else:
         raise Exception("No chunks expected.")
         
    if not chunks:
        raise Exception("No chunks found to merge.")

    # 3. Create file list for FFmpeg
    # Format: file 'path/to/file.wav'
    list_path = os.path.join(base_dir, "mylist.txt")
    with open(list_path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            # Escape single quotes in path if any?
            # FFmpeg concat demuxer requires escaping.
            # Ideally use relative paths or simple paths.
            # Windows paths with backslashes need care. Forward slashes usually work best with FFmpeg.
            # Since mylist.txt is in the same dir as chunks, we should use just the filename
            # to avoid path duplication (FFmpeg treats paths relative to the list file).
            filename = os.path.basename(chunk)
            f.write(f"file '{filename}'\n")
            
    # 4. Run FFmpeg
    # Output dir: ../final/
    final_dir = os.path.join(os.path.dirname(base_dir), "final")
    os.makedirs(final_dir, exist_ok=True)
    
    
    output_wav = os.path.join(final_dir, f"{base_name}_final.wav")
    
    ffmpeg_exe = "ffmpeg"
    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass

    # Command: ffmpeg -f concat -safe 0 -i mylist.txt -c copy output.wav
    cmd = [
        ffmpeg_exe,
        "-f", "concat",
        "-safe", "0",
        "-i", list_path,
        "-c", "copy",
        "-y", # Overwrite
        output_wav
    ]
    
    try:
        # CREATE_NO_WINDOW = 0x08000000
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True, creationflags=0x08000000)
    except subprocess.CalledProcessError as e:
        raise Exception(f"FFmpeg merge failed: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        
    return output_wav
