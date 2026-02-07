import subprocess
import os

def convert_wav_to_mp3(wav_path):
    """
    Converts a WAV file to MP3 using FFmpeg.
    
    Args:
        wav_path (str): Path to the source WAV file.
        
    Returns:
        str: Path to the generated MP3 file.
        
    Raises:
        Exception: If file not found or FFmpeg fails.
    """
    
    if not os.path.exists(wav_path):
        raise Exception(f"Input WAV file not found: {wav_path}")
        
    # Construct output path
    # output/Doc/final/doc.wav -> output/Doc/final/doc.mp3
    base, _ = os.path.splitext(wav_path)
    mp3_path = f"{base}.mp3"
    
    # FFmpeg command
    # ffmpeg -i input.wav -codec:a libmp3lame -qscale:a 2 output.mp3
    cmd = [
        "ffmpeg",
        "-i", wav_path,
        "-codec:a", "libmp3lame",
        "-qscale:a", "2", # VBR High Quality
        "-y", # Overwrite
        mp3_path
    ]
    
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"FFmpeg MP3 conversion failed: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        
    if not os.path.exists(mp3_path):
        raise Exception("FFmpeg ran but MP3 file was not created.")
        
    return mp3_path
