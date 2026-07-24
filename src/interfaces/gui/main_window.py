"""Main window — Phase 4: full pipeline with progress, cancel, preview."""

import os
import threading
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QSizePolicy, QApplication, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QDragEnterEvent, QDropEvent

from src.domain.models.voice_settings import VoiceSettings
from src.interfaces.gui.widgets.sidebar import Sidebar
from src.interfaces.gui.widgets.toolbar import Toolbar
from src.interfaces.gui.widgets.editor import Editor
from src.interfaces.gui.widgets.action_panel import ActionPanel
from src.interfaces.gui.widgets.progress_bar import ProgressBar
from src.interfaces.gui.widgets.log_console import LogConsole
from src.interfaces.gui.styles.palette import DARK_PALETTE, LIGHT_PALETTE
from src.interfaces.gui.signals import QtJournalBridge, WorkerSignals
from src.infrastructure.container import Container
from src.infrastructure.env_manager import open_path


# ── Volume conversion helpers (single source of truth) ──────────────

def _slider_to_vol(slider_value: int) -> float:
    """Convert 0-100 slider int → 0.0-1.0 float for config/FFmpeg."""
    return max(0.0, min(1.0, slider_value / 100.0))


def _vol_to_slider(vol: float) -> int:
    """Convert 0.0-1.0 float (config/FFmpeg) → 0-100 slider int."""
    return max(0, min(100, round(vol * 100)))


# ── Theme / stylesheet loader ──────────────────────────────────────

def load_stylesheet(palette: dict) -> str:
    """Load theme.qss and interpolate palette colors."""
    qss_path = os.path.join(os.path.dirname(__file__), "styles", "theme.qss")
    with open(qss_path, "r") as f:
        template = f.read()
    return template.format(**palette)


def _enable_styled_background(widget):
    widget.setAttribute(Qt.WA_StyledBackground, True)


# ── Supported file extensions (must match DocumentExtractorResolver) ─

SUPPORTED_EXTENSIONS = (".pdf", ".md", ".markdown", ".txt")
FILE_DIALOG_FILTER = (
    "Documentos soportados (*.pdf *.md *.markdown *.txt);;"
    "PDF (*.pdf);;Markdown (*.md *.markdown);;Texto (*.txt)"
)


class MainWindow(QMainWindow):
    """PDF To Speech Studio — PySide6 main window (Phase 3)."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF To Speech Studio v4.1")
        self.setMinimumSize(1000, 700)
        self.resize(1100, 850)

        # Enable drops on the whole window
        self.setAcceptDrops(True)

        # ── Infrastructure ──
        self.container = Container()
        self.config = self.container.config_repo
        self._bgm_path = None
        self._history = list(self.config.get("history", []))

        # ── File loading state ──
        self._current_file_path: str | None = None
        self._extracted_text: str = ""

        # ── Pipeline cancel event ──
        self._cancel_event = threading.Event()

        # ── Worker signals (cross-thread extraction) ──
        self._worker_signals = WorkerSignals()
        self._worker_signals.extraction_complete.connect(self._on_extraction_complete)
        self._worker_signals.error.connect(self._on_extraction_error)

        # ── Pipeline signals (progress, finish, error) ──
        self._pipeline_signals = WorkerSignals()
        self._pipeline_signals.progress.connect(self._on_pipeline_progress)
        self._pipeline_signals.finished.connect(self._on_pipeline_finished)
        self._pipeline_signals.error.connect(self._on_pipeline_error)

        # ── Preview signals ──
        self._preview_signals = WorkerSignals()
        self._preview_signals.finished.connect(self._on_preview_finished)
        self._preview_signals.error.connect(self._on_preview_error)

        # ── Central widget + root layout ──
        central = QWidget()
        self.setCentralWidget(central)
        _enable_styled_background(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Sidebar ──
        self.sidebar = Sidebar()
        root_layout.addWidget(self.sidebar)

        # ── Main area ──
        self.main_area = QFrame()
        self.main_area.setObjectName("main_area")
        _enable_styled_background(self.main_area)
        main_layout = QVBoxLayout(self.main_area)
        main_layout.setContentsMargins(20, 20, 20, 40)
        main_layout.setSpacing(12)

        self.toolbar = Toolbar()
        main_layout.addWidget(self.toolbar)

        self.editor = Editor()
        main_layout.addWidget(self.editor)

        self.action_panel = ActionPanel()
        main_layout.addWidget(self.action_panel)

        self.progress = ProgressBar()
        main_layout.addWidget(self.progress)

        self.log_console = LogConsole()
        main_layout.addWidget(self.log_console)

        main_layout.addStretch()
        root_layout.addWidget(self.main_area, stretch=1)

        # ── Restore sidebar state from config ──
        self._restore_sidebar_state()

        # ── Apply theme from saved preference (BEFORE show) ──
        mode = self.config.get("appearance_mode", "Dark")
        self._current_mode = mode
        self._apply_theme(DARK_PALETTE if mode == "Dark" else LIGHT_PALETTE)

        # ── Connect all signals ──
        self._connect_signals()

        # ── Journal bridge → Bitácora (thread-safe) ──
        self.log_bridge = QtJournalBridge(self.container.journal_adapter)
        self.log_bridge.message_received.connect(self.log_console.append)

        # ── Initial action state: no text yet ──
        self._update_action_states()

    # ── Supported file check ───────────────────────────────────────

    @staticmethod
    def _is_supported_file(path: str) -> bool:
        """Check whether the file extension is supported by the resolver."""
        return path.lower().endswith(SUPPORTED_EXTENSIONS)

    # ── Restore ────────────────────────────────────────────────────

    def _restore_sidebar_state(self):
        mode = self.config.get("appearance_mode", "Dark")
        self.sidebar.set_theme_mode(mode)
        voice_vol = self.config.get("voice_vol", 1.0)
        bgm_vol = self.config.get("bgm_vol", 0.2)
        self.sidebar.set_volume_values(
            _vol_to_slider(voice_vol), _vol_to_slider(bgm_vol)
        )
        self.sidebar.update_history(self._history)

    # ── Theme ──────────────────────────────────────────────────────

    def _apply_fonts(self):
        ui_font = QFont("Inter", 13)
        ui_font.setStyleHint(QFont.SansSerif)
        QApplication.instance().setFont(ui_font)

    def _apply_theme(self, palette):
        stylesheet = load_stylesheet(palette)
        QApplication.instance().setStyleSheet(stylesheet)

    # ── Signal wiring ──────────────────────────────────────────────

    def _connect_signals(self):
        self.sidebar.theme_toggled.connect(self._on_theme_toggle)
        self.sidebar.log_toggle_requested.connect(self._on_log_toggle)
        self.toolbar.edit_toggled.connect(self._on_edit_toggle)

        # Mixer persistence
        self.sidebar.slider_v_vol.valueChanged.connect(self._on_voice_vol_changed)
        self.sidebar.slider_b_vol.valueChanged.connect(self._on_bgm_vol_changed)

        # Sidebar actions
        self.sidebar.clear_cache_requested.connect(self._on_clear_cache)
        self.sidebar.load_bgm_requested.connect(self._on_load_bgm)
        self.sidebar.load_file_requested.connect(self._on_load_file)

        # Toolbar actions
        self.toolbar.load_file_requested.connect(self._on_load_file_clicked)
        self.toolbar.select_destination_requested.connect(self._on_select_destination)

        # Pipeline actions (Phase 4)
        self.action_panel.start_requested.connect(self._on_start_process)
        self.action_panel.stop_requested.connect(self._on_stop_process)
        self.action_panel.preview_requested.connect(self._on_preview)

    # ── Theme handler ──────────────────────────────────────────────

    def _on_theme_toggle(self, mode):
        self._current_mode = mode
        palette = DARK_PALETTE if mode == "Dark" else LIGHT_PALETTE
        self._apply_theme(palette)
        self.config.set("appearance_mode", mode)

    def _on_log_toggle(self):
        self.log_console.toggle_console()

    def _on_edit_toggle(self, checked):
        if checked:
            self.editor.show_editor()
        else:
            self.editor.hide_editor()

    # ── Mixer persistence ──────────────────────────────────────────

    def _on_voice_vol_changed(self, value):
        self.config.set("voice_vol", _slider_to_vol(value))

    def _on_bgm_vol_changed(self, value):
        self.config.set("bgm_vol", _slider_to_vol(value))

    # ── Clear cache ────────────────────────────────────────────────

    def _on_clear_cache(self):
        reply = QMessageBox.question(
            self, "Limpiar Cache",
            "Se eliminarán todos los archivos de audio cacheados.\n"
            "La próxima vez que procese un documento, se regenerará el audio.\n\n"
            "¿Continuar?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.container.cache_repo.clear()
                self.log_console.append("[OK] Cache limpiada correctamente.")
            except Exception as e:
                self.log_console.append(f"[ERROR] Error al limpiar cache: {e}")

    # ── Load background music ──────────────────────────────────────

    def _on_load_bgm(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar música de fondo", "", "Audio MP3 (*.mp3)"
        )
        if path:
            if not path.lower().endswith(".mp3"):
                self.log_console.append(
                    "[WARN] Formato no soportado: solo MP3. Seleccioná un archivo .mp3."
                )
                return
            self._bgm_path = path
            self.log_console.append(
                f"[OK] Música de fondo cargada: {os.path.basename(path)}"
            )

    # ── History: file load from sidebar click ──────────────────────

    def _on_load_file(self, path):
        """Handle history-item click: load file (same flow as button/drop)."""
        if not os.path.exists(path):
            QMessageBox.warning(self, "Archivo no encontrado",
                                f"El archivo ya no existe:\n{path}")
            try:
                self._history.remove(path)
            except ValueError:
                pass
            self.config.set("history", self._history)
            self.sidebar.update_history(self._history)
            return

        if self._check_dirty_before_load():
            self._start_extraction(path)

    # ── Toolbar: load file button ──────────────────────────────────

    def _on_load_file_clicked(self):
        """Open file dialog → check dirty → start extraction."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo", "", FILE_DIALOG_FILTER
        )
        if path and self._check_dirty_before_load():
            self._start_extraction(path)

    # ── Toolbar: select destination folder ─────────────────────────

    def _on_select_destination(self):
        path = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta de destino",
            self.config.get("output_path", "")
        )
        if path:
            self.config.set("output_path", path)
            self.log_console.append(f"[OK] Carpeta de destino: {path}")

    # ── Dirty check ────────────────────────────────────────────────

    def _check_dirty_before_load(self) -> bool:
        """If the editor has unsaved edits, ask before discarding. True = proceed."""
        if not self._extracted_text:
            return True  # Nothing to lose
        current = self.editor.get_content()
        if current == self._extracted_text:
            return True  # Not modified
        reply = QMessageBox.question(
            self, "Cambios sin guardar",
            "Hay cambios sin guardar en el editor.\n"
            "¿Cargar el nuevo archivo? Los cambios se perderán.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        return reply == QMessageBox.Yes

    # ── Extraction worker ──────────────────────────────────────────

    def _start_extraction(self, path: str):
        """Launch extraction in a background thread (cross-thread via signals)."""
        self._current_file_path = path
        self.toolbar.set_file_label(os.path.basename(path))
        self.toolbar.set_edit_enabled(False)
        self.editor.hide_editor()

        signals = self._worker_signals
        extractor = self.container.extractor
        journal = self.container.journal_adapter

        def _extract():
            try:
                if not extractor.supports(path):
                    signals.error.emit(
                        f"Formato no soportado: {os.path.basename(path)}"
                    )
                    return
                journal.info(f"Extrayendo texto de: {os.path.basename(path)}")
                text, meta = extractor.extract_text(path)
                signals.extraction_complete.emit(text)
            except Exception as exc:
                signals.error.emit(str(exc))

        thread = threading.Thread(target=_extract, daemon=True)
        thread.start()

    def _update_action_states(self):
        """Enable/disable pipeline and preview buttons based on text availability."""
        has_text = bool(self._extracted_text)
        self.action_panel.set_actions_enabled(has_text)

    def _on_extraction_complete(self, text: str):
        """Handle extracted text on the main thread."""
        if not text:
            self._on_extraction_error(
                "No se pudo extraer texto. El archivo podría estar vacío, "
                "ser un escaneo sin OCR funcional, o estar protegido."
            )
            return

        self._extracted_text = text
        self.editor.set_content(text)
        self.editor.hide_editor()  # Only show when user enables edit mode
        self.toolbar.set_edit_enabled(True)
        self._update_action_states()

        # Update history
        if self._current_file_path:
            self._add_to_history(self._current_file_path)

        self.log_console.append(
            f"[OK] Texto extraído ({len(text)} caracteres)"
        )

    def _on_extraction_error(self, err_msg: str):
        """Handle extraction error on the main thread."""
        self._current_file_path = None
        self._extracted_text = ""
        self.toolbar.set_file_label("Error al cargar archivo", loaded=False)
        self.toolbar.set_edit_enabled(False)
        self._update_action_states()
        self.log_console.append(f"[ERROR] {err_msg}")

    # ── History management ─────────────────────────────────────────

    def _add_to_history(self, path):
        if path in self._history:
            self._history.remove(path)
        self._history.insert(0, path)
        self._history = self._history[:10]
        self.config.set("history", self._history)
        self.sidebar.update_history(self._history)

    # ── Drag & drop (native Qt) ────────────────────────────────────

    def _reset_drag_style(self):
        """Remove drag-over visual feedback."""
        self.main_area.setProperty("dragActive", False)
        self.main_area.style().unpolish(self.main_area)
        self.main_area.style().polish(self.main_area)

    def _apply_drag_style(self):
        """Show drag-over visual feedback."""
        self.main_area.setProperty("dragActive", True)
        self.main_area.style().unpolish(self.main_area)
        self.main_area.style().polish(self.main_area)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            path = url.toLocalFile()
            if self._is_supported_file(path):
                self._apply_drag_style()
                event.acceptProposedAction()
                return
        event.ignore()

    def dragMoveEvent(self, event):
        # Accept while still dragging so the OS shows a valid-drop cursor
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            path = url.toLocalFile()
            if self._is_supported_file(path):
                event.acceptProposedAction()
                return
        event.ignore()

    def dragLeaveEvent(self, event):
        self._reset_drag_style()
        event.accept()

    def dropEvent(self, event: QDropEvent):
        self._reset_drag_style()

        if not event.mimeData().hasUrls():
            event.ignore()
            return

        path = event.mimeData().urls()[0].toLocalFile()

        if not self._is_supported_file(path):
            self.log_console.append(
                f"[WARN] Formato no soportado: {os.path.basename(path)}. "
                f"Usá PDF, Markdown o TXT."
            )
            event.ignore()
            return

        if not self._check_dirty_before_load():
            # User cancelled — reset drag state cleanly
            event.ignore()
            return

        event.acceptProposedAction()
        self._start_extraction(path)

    # ═════════════════════════════════════════════════════════════════
    # PHASE 4 — Pipeline: process, progress, cancel, preview
    # ═════════════════════════════════════════════════════════════════

    # ── Start process ───────────────────────────────────────────────

    def _on_start_process(self):
        """Launch the full TTS pipeline in a background thread."""
        journal = self.container.journal_adapter
        text = (self.editor.get_content()
                if self.editor.isVisible()
                else self._extracted_text)
        if not text:
            journal.warning("No hay texto para procesar. Cargá un archivo primero.")
            return
        if not self._current_file_path:
            journal.warning("No hay archivo cargado.")
            return

        output_path = self.config.get("output_path", os.path.join(os.getcwd(), "output"))
        if not output_path or not os.path.isdir(output_path):
            journal.warning("No hay carpeta de destino. Seleccioná una en el toolbar.")
            return

        # Read UI settings with volume conversion (UI 0‑100 → float 0.0‑1.0)
        settings = VoiceSettings(
            voice_id=self.action_panel.get_voice(),
            rate=f"{self.action_panel.get_rate():+d}%",
            pitch=f"{self.action_panel.get_pitch():+d}Hz",
            volume=_slider_to_vol(self.sidebar.slider_v_vol.value()),
        )
        bgm_vol = _slider_to_vol(self.sidebar.slider_b_vol.value())

        self._cancel_event.clear()
        self.action_panel.set_process_loading(True)
        journal.info("Iniciando proceso...")

        thread = threading.Thread(
            target=self._run_pipeline,
            args=(text, output_path, settings, bgm_vol),
            daemon=True,
        )
        thread.start()

    def _run_pipeline(self, text, output_path, settings, bgm_vol):
        """Worker: run the use case and emit signals from the background thread."""
        signals = self._pipeline_signals
        use_case = self.container.process_pdf_use_case
        try:
            final_path = use_case.execute(
                text=text,
                pdf_path=self._current_file_path,
                output_base_dir=output_path,
                voice_settings=settings,
                bgm_path=self._bgm_path,
                bgm_volume=bgm_vol,
                progress_callback=lambda msg, val: signals.progress.emit(msg, val),
                cancel_event=self._cancel_event,
            )
            if final_path:
                signals.finished.emit(final_path)
            else:
                signals.finished.emit("")  # cancelled
        except Exception as exc:
            signals.error.emit(str(exc))

    def _on_pipeline_progress(self, msg: str, val: float):
        """Update progress meter and status label (main thread)."""
        self.progress.set_progress(val)
        self.progress.set_status(msg)

    def _on_pipeline_finished(self, path: str):
        """Handle pipeline completion (main thread)."""
        self.action_panel.set_process_loading(False)

        if path:
            self.progress.set_status("¡Completado!")
            self.log_console.append(f"[OK] Audio generado: {os.path.basename(path)}")
            self.config.set("last_output", path)
            reply = QMessageBox.question(
                self, "Éxito",
                "El audio se generó correctamente.\n¿Deseas escucharlo?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes,
            )
            if reply == QMessageBox.Yes:
                open_path(path)
        else:
            self.progress.set_status("Cancelado")
            self.log_console.append("[WARN] Proceso cancelado por el usuario.")
            self.progress.reset()

    def _on_pipeline_error(self, err_msg: str):
        """Handle pipeline error (main thread)."""
        self.action_panel.set_process_loading(False)
        self.progress.set_status("Error")
        self.progress.reset()
        self.log_console.append(f"[ERROR] {err_msg}")

    # ── Stop / cancel ───────────────────────────────────────────────

    def _on_stop_process(self):
        """Request pipeline cancellation."""
        self._cancel_event.set()
        self.container.journal_adapter.warning("Cancelación solicitada — terminando chunks pendientes...")

    # ── Preview voice ───────────────────────────────────────────────

    def _on_preview(self):
        """Generate a short voice preview in a background thread."""
        text = (self.editor.get_content()
                if self.editor.isVisible()
                else self._extracted_text)
        if not text:
            self.container.journal_adapter.warning("No hay texto para previsualizar. Cargá un archivo primero.")
            return

        settings = VoiceSettings(
            voice_id=self.action_panel.get_voice(),
            rate=f"{self.action_panel.get_rate():+d}%",
            pitch=f"{self.action_panel.get_pitch():+d}Hz",
            volume=_slider_to_vol(self.sidebar.slider_v_vol.value()),
        )

        self.action_panel.set_preview_loading(True)
        self.container.journal_adapter.info("Generando preview de voz...")

        thread = threading.Thread(
            target=self._run_preview,
            args=(text, settings),
            daemon=True,
        )
        thread.start()

    def _run_preview(self, text, settings):
        """Worker: generate preview and emit finished signal."""
        try:
            path = self.container.process_pdf_use_case.preview_voice(text, settings)
            self._preview_signals.finished.emit(path)
        except Exception as exc:
            self._preview_signals.error.emit(str(exc))

    def _on_preview_finished(self, path: str):
        """Handle preview completion (main thread)."""
        self.action_panel.set_preview_loading(False)
        self.log_console.append(f"[OK] Preview generado: {os.path.basename(path)}")
        open_path(path)

    def _on_preview_error(self, err_msg: str):
        """Handle preview error (main thread)."""
        self.action_panel.set_preview_loading(False)
        self.log_console.append(f"[ERROR] Preview: {err_msg}")
