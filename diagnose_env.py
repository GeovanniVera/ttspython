import shutil
import subprocess
import sys
import os

print("--- Diagnostics ---")
ffmpeg_path = shutil.which("ffmpeg")
edge_tts_path = shutil.which("edge-tts")
print(f"FFmpeg path: {ffmpeg_path}")
print(f"edge-tts path: {edge_tts_path}")

print(f"Python executable: {sys.executable}")
print(f"PATH: {os.environ.get('PATH')}")

try:
    subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("FFmpeg executability: OK")
except Exception as e:
    print(f"FFmpeg executability: FAIL ({e})")

try:
    subprocess.run(["edge-tts", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("edge-tts executability: OK")
except Exception as e:
    print(f"edge-tts executability: FAIL ({e})")
