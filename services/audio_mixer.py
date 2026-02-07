import subprocess
import os
import sys

def get_ffmpeg_exe():
    """
    Locates the FFmpeg executable.
    Prioritizes the bundled version in sys._MEIPASS for PyInstaller compatibility.
    Falls back to imageio_ffmpeg or system PATH.
    """
    # 1. Check if running in PyInstaller bundle
    if hasattr(sys, '_MEIPASS'):
        # In the one-file mode, everything is unpacked to sys._MEIPASS
        bundled_ffmpeg = os.path.join(sys._MEIPASS, "ffmpeg.exe")
        if os.path.exists(bundled_ffmpeg):
            return bundled_ffmpeg

    # 2. Development mode / Fallback
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass

    # 3. System PATH
    return "ffmpeg"

def mix_audio(voice_path, bgm_path, output_path, voice_vol=1.0, bgm_vol=0.2):
    """
    Mixes voice audio with a background music track.
    
    Args:
        voice_path (str): Path to the voice WAV file.
        bgm_path (str): Path to the background music file.
        output_path (str): Path to save the mixed audio.
        voice_vol (float): Volume multiplier for voice (default 1.0).
        bgm_vol (float): Volume multiplier for music (default 0.2).
        
    Returns:
        str: Path to the mixed audio file.
        
    Raises:
        Exception: If FFmpeg fails or inputs are missing.
    """
    
    if not os.path.exists(voice_path):
        raise Exception(f"Voice file not found: {voice_path}")
    if not os.path.exists(bgm_path):
        raise Exception(f"Background music file not found: {bgm_path}")
        
    ffmpeg_exe = get_ffmpeg_exe()
    
    # Construct FFmpeg command
    # -stream_loop -1: Loop the input 1 (bgm) infinitely
    # Inputs:
    # 0: Voice
    # 1: BGM
    # Filter:
    # [0:a]volume={voice_vol}[v] -> adjust voice volume
    # [1:a]volume={bgm_vol}[b] -> adjust bgm volume
    # [v][b]amix=inputs=2:duration=first[out] -> mix them, stopping when the first input (voice) ends
    
    filter_complex = f"[0:a]volume={voice_vol}[v];[1:a]volume={bgm_vol}[b];[v][b]amix=inputs=2:duration=first[out]"

    cmd = [
        ffmpeg_exe,
        "-i", voice_path,
        "-stream_loop", "-1",
        "-i", bgm_path,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-y", # Overwrite output
        output_path
    ]
    
    # Execution flags to hide window on Windows
    # STARTF_USESHOWWINDOW = 0x00000001
    # DETACHED_PROCESS = 0x00000008 (not strictly needed if using CREATE_NO_WINDOW)
    # CREATE_NO_WINDOW = 0x08000000
    
    creation_flags = 0x08000000
    
    try:
        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=True,
            creationflags=creation_flags
        )
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode().strip() if e.stderr else "Unknown error"
        raise Exception(f"FFmpeg mixing failed: {error_msg}")
        
    if not os.path.exists(output_path):
        raise Exception("FFmpeg ran but mixed file was not created.")
        
    return output_path
