"""Phase 4 screenshot: run pipeline twice, show cache hit in Bitácora.

Usage: python tests/take_screenshot.py
"""

import sys, os, time, threading, tempfile, shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.pop("QT_QPA_PLATFORM", None)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QWindow
from PySide6.QtGui import QImage

# ── Mock TTS ──
class FakeGenerator:
    def __init__(self):
        self.call_count = 0
    def generate_speech(self, text, path, settings):
        self.call_count += 1
        with open(path, "wb") as f:
            f.write(b"fake mp3 data for screenshot")

from src.infrastructure.repositories.cache_repository import CacheRepository
from src.infrastructure.adapters.ffmpeg_adapter import FFmpegAdapter
from src.infrastructure.adapters.journal_adapter import JournalAdapter
from src.domain.services.text_service import TextService
from src.application.use_cases.process_pdf_to_speech import ProcessPdfToSpeechUseCase
from src.domain.models.voice_settings import VoiceSettings
from unittest.mock import MagicMock

tmp = tempfile.mkdtemp(suffix="_screenshot_demo")
cache = CacheRepository(cache_dir=os.path.join(tmp, "cache"))
out_dir = os.path.join(tmp, "output")
os.makedirs(out_dir, exist_ok=True)

gen = FakeGenerator()
journal = JournalAdapter()

use_case = ProcessPdfToSpeechUseCase(
    extractor=MagicMock(),
    generator=gen,
    processor=FFmpegAdapter(),
    text_service=TextService(),
    cache_repo=cache,
    journal=journal,
    max_workers=4,
)
use_case.processor.merge_wavs = lambda paths, out: out
use_case.processor.mix_with_bgm = lambda v, b, out, vv, bv: out

LONG_TEXT = (
    "La inteligencia artificial está transformando la forma en que interactuamos con la tecnología. "
    "Cada día surgen nuevas herramientas que nos permiten ser más productivos y creativos. "
    "En el campo del procesamiento de audio, los avances han sido particularmente notables. "
    "Los sistemas de texto a voz han mejorado significativamente en los últimos años. "
) * 120

settings = VoiceSettings(
    voice_id="es-MX-JorgeNeural",
    rate="+0%",
    pitch="+0Hz",
    volume=0.8,
)

app = QApplication(sys.argv)

from src.interfaces.gui.main_window import MainWindow
from src.interfaces.gui.signals import QtJournalBridge

window = MainWindow()

# Seed state
window._current_file_path = os.path.join(tmp, "demo.pdf")
window._extracted_text = LONG_TEXT
window.editor.set_content(LONG_TEXT)
window.container.config_repo.set("output_path", out_dir)
window._bgm_path = None

# Override with test use case
window.container.process_pdf_use_case = use_case
window.container.speech_generator = gen
window.container.cache_repo = cache

# Re-bridge journal
window.log_bridge = QtJournalBridge(journal)
window.log_bridge.message_received.connect(window.log_console.append)

window.show()
app.processEvents()
time.sleep(0.5)
window.log_console.show_console()
app.processEvents()
time.sleep(0.3)

def take_screenshot(path):
    """Capture the main window content using Qt's widget grab."""
    try:
        pixmap = window.grab()
        pixmap.save(path, "PNG")
        return True
    except Exception as e:
        print(f"  Screenshot error: {e}")
        return False

def run_pipeline(label):
    print(f"\n  >>> {label}")
    window.progress.reset()
    window.log_console.clear()
    window._cancel_event.clear()
    app.processEvents()

    def _run():
        try:
            final_path = use_case.execute(
                text=LONG_TEXT,
                pdf_path=window._current_file_path,
                output_base_dir=out_dir,
                voice_settings=settings,
                bgm_path=None,
                bgm_volume=0.2,
                progress_callback=lambda msg, val: window._pipeline_signals.progress.emit(msg, val),
                cancel_event=window._cancel_event,
            )
            if final_path:
                window._pipeline_signals.finished.emit(final_path)
            else:
                window._pipeline_signals.finished.emit("")
        except Exception as exc:
            window._pipeline_signals.error.emit(str(exc))

    window.action_panel.set_process_loading(True)
    threading.Thread(target=_run, daemon=True).start()

    for _ in range(300):
        app.processEvents()
        time.sleep(0.02)
        if not window.action_panel.btn_process.is_loading():
            break
    app.processEvents()
    time.sleep(0.3)

# Run 1
run_pipeline("RUN 1 — SIN CACHE")

# Run 2
run_pipeline("RUN 2 — CACHE HITS")

# Screenshot
sdir = os.path.join(os.path.dirname(__file__), "..", "design")
os.makedirs(sdir, exist_ok=True)
screenshot = os.path.join(sdir, "fase4_cache_hit.png")
ok = take_screenshot(screenshot)

n_chunks = len(TextService().chunk_text(LONG_TEXT))
print(f"\n  Screenshot: {screenshot} {'✓' if ok else '✗'}")
print(f"  Chunks: {n_chunks}")
print(f"  TTS calls total (2 runs): {gen.call_count}")
print(f"  Expected: {n_chunks} (no new calls on run 2)")
print(f"  Cache: {'✓ HIT' if gen.call_count <= n_chunks else '✗ MISS'}")

shutil.rmtree(tmp)
print("  Done.")
