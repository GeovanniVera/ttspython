import os
import subprocess
import sys
import shutil
from typing import List
from src.domain.ports.audio_processor import AudioProcessorPort

class FFmpegAdapter(AudioProcessorPort):
    def __init__(self):
        self.ffmpeg_exe = self._get_ffmpeg_exe()

    def _get_ffmpeg_exe(self):
        if hasattr(sys, '_MEIPASS'):
            bundled_ffmpeg = os.path.join(sys._MEIPASS, "ffmpeg.exe")
            if os.path.exists(bundled_ffmpeg):
                return bundled_ffmpeg
        try:
            import imageio_ffmpeg
            return imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError:
            return "ffmpeg"

    def merge_wavs(self, file_paths: List[str], output_path: str) -> str:
        """Concatenates audio files (MP3 or WAV) and re-encodes to ensure consistent metadata."""
        if not file_paths:
            raise ValueError("No hay archivos para unir.")
        
        # Ensure output is MP3
        if output_path.endswith('.wav'):
            output_path = output_path.replace('.wav', '.mp3')

        list_file = output_path + ".list.txt"
        with open(list_file, "w", encoding="utf-8") as f:
            for p in file_paths:
                abs_p = os.path.abspath(p).replace("\\", "/")
                f.write(f"file '{abs_p}'\n")

        cmd = [
            self.ffmpeg_exe,
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-codec:a", "libmp3lame", # Re-encoding is safer for duration metadata
            "-qscale:a", "4",
            "-y",
            output_path
        ]
        
        try:
            creation_flags = 0x08000000 if os.name == 'nt' else 0
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True, creationflags=creation_flags)
        finally:
            if os.path.exists(list_file):
                os.remove(list_file)
        
        return output_path

    def mix_with_bgm(self, voice_path: str, bgm_path: str, output_path: str, voice_vol: float, bgm_vol: float) -> str:
        """Mixes voice audio with optional background music."""
        # Ensure output is MP3
        if output_path.endswith('.wav'):
            output_path = output_path.replace('.wav', '.mp3')

        creation_flags = 0x08000000 if os.name == 'nt' else 0

        # Check if background music exists
        if not bgm_path or not os.path.exists(bgm_path):
            # No background music, just process voice
            if abs(voice_vol - 1.0) < 0.01 and voice_path.lower().endswith('.mp3'):
                # Optimization: if already MP3 and volume is 1.0, just copy
                if os.path.abspath(voice_path) != os.path.abspath(output_path):
                    shutil.copy2(voice_path, output_path)
                return output_path
            
            cmd = [
                self.ffmpeg_exe,
                "-i", voice_path,
                "-filter:a", f"volume={voice_vol}",
                "-codec:a", "libmp3lame",
                "-qscale:a", "4",
                "-y",
                output_path
            ]
        else:
            # Both voice and BGM exist, mix them
            filter_complex = f"[0:a]volume={voice_vol}[v];[1:a]volume={bgm_vol}[b];[v][b]amix=inputs=2:duration=first[out]"
            cmd = [
                self.ffmpeg_exe,
                "-i", voice_path,
                "-stream_loop", "-1",
                "-i", bgm_path,
                "-filter_complex", filter_complex,
                "-map", "[out]",
                "-codec:a", "libmp3lame",
                "-qscale:a", "4", # High quality VBR
                "-y",
                output_path
            ]
        
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True, creationflags=creation_flags)
        return output_path

    def convert_to_mp3(self, input_path: str) -> str:
        """Utility to convert any format to MP3 if needed."""
        if input_path.endswith('.mp3'):
            return input_path
            
        output_path = input_path.rsplit('.', 1)[0] + ".mp3"
        cmd = [
            self.ffmpeg_exe,
            "-i", input_path,
            "-codec:a", "libmp3lame",
            "-qscale:a", "4",
            "-y",
            output_path
        ]
        creation_flags = 0x08000000 if os.name == 'nt' else 0
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True, creationflags=creation_flags)
        return output_path

    def generate_silence(self, duration: float, output_path: str) -> str:
        """Generates a silent MP3 file of the given duration."""
        cmd = [
            self.ffmpeg_exe,
            "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=stereo",
            "-t", str(duration),
            "-codec:a", "libmp3lame",
            "-y",
            output_path
        ]
        creation_flags = 0x08000000 if os.name == 'nt' else 0
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True, creationflags=creation_flags)
        return output_path
