"""Sidebar widget: branding, theme toggle, history, mixer, cache."""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCheckBox, QFrame,
    QSlider, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from src.interfaces.gui.widgets.shadow_button import ShadowButton


def _enable_styled_background(widget):
    widget.setAttribute(Qt.WA_StyledBackground, True)


class Sidebar(QWidget):
    """Left sidebar with theme toggle, history, audio mixer, and cache."""

    theme_toggled = Signal(str)  # emits "Dark" or "Light"
    load_file_requested = Signal(str)
    load_bgm_requested = Signal()
    clear_cache_requested = Signal()
    log_toggle_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(280)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        _enable_styled_background(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(0)

        # --- Title (Source Serif 4, display) ---
        title = QLabel("Text to Speech GUI")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(12)

        # --- Theme Toggle (pill switch) ---
        self.theme_switch = QCheckBox("Modo Oscuro")
        self.theme_switch.setObjectName("theme_switch")
        self.theme_switch.setChecked(True)
        self.theme_switch.setAutoFillBackground(False)
        self.theme_switch.clicked.connect(self._on_theme_clicked)
        layout.addWidget(self.theme_switch, alignment=Qt.AlignCenter)
        layout.addSpacing(16)

        # --- History Section ---
        history_label = QLabel("Recientes")
        history_label.setObjectName("section")
        history_label.setContentsMargins(10, 0, 10, 4)
        layout.addWidget(history_label)

        self.history_container = QFrame()
        self.history_container.setObjectName("history_container")
        _enable_styled_background(self.history_container)
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setContentsMargins(10, 4, 10, 4)
        self.history_layout.setSpacing(2)
        # No addStretch — empty container collapses naturally
        layout.addWidget(self.history_container)

        # --- Mixer Card (flows directly after Recientes) ---
        self.mixer_card = QFrame()
        self.mixer_card.setObjectName("mixer_card")
        _enable_styled_background(self.mixer_card)
        mixer_layout = QVBoxLayout(self.mixer_card)
        mixer_layout.setContentsMargins(20, 16, 20, 16)
        mixer_layout.setSpacing(8)

        mixer_title = QLabel("Mezcla de Audio")
        mixer_title.setObjectName("section")
        mixer_layout.addWidget(mixer_title)
        mixer_layout.addSpacing(4)

        # Voice volume — teal slider
        self.lbl_v_vol = QLabel("Voz")
        self.lbl_v_vol.setObjectName("mixer_label")
        mixer_layout.addWidget(self.lbl_v_vol)

        self.val_v_vol = QLabel("100%")
        self.val_v_vol.setObjectName("mixer_value")

        v_vol_row = QWidget()
        v_vol_row.setAutoFillBackground(False)
        v_vol_row.setStyleSheet("background-color: transparent;")
        v_vol_row_lay = QVBoxLayout(v_vol_row)
        v_vol_row_lay.setContentsMargins(0, 0, 0, 0)
        v_vol_row_lay.setSpacing(2)

        hdr_v = QWidget()
        hdr_v.setAutoFillBackground(False)
        hdr_v.setStyleSheet("background-color: transparent;")
        hdr_v_lay = QVBoxLayout(hdr_v)
        hdr_v_lay.setContentsMargins(0, 0, 0, 0)
        hdr_v_lay.setSpacing(0)
        hdr_v_lay.addWidget(self.lbl_v_vol)
        hdr_v_lay.addWidget(self.val_v_vol)

        self.slider_v_vol = QSlider(Qt.Horizontal)
        self.slider_v_vol.setObjectName("slider_teal")
        self.slider_v_vol.setRange(0, 100)
        self.slider_v_vol.setValue(100)
        self.slider_v_vol.valueChanged.connect(
            lambda v: self.val_v_vol.setText(f"{v}%")
        )

        mixer_layout.addWidget(hdr_v)
        mixer_layout.addWidget(self.slider_v_vol)

        # BGM volume — teal slider
        self.lbl_b_vol = QLabel("Musica")
        self.lbl_b_vol.setObjectName("mixer_label")
        mixer_layout.addWidget(self.lbl_b_vol)

        self.val_b_vol = QLabel("20%")
        self.val_b_vol.setObjectName("mixer_value")

        hdr_b = QWidget()
        hdr_b.setAutoFillBackground(False)
        hdr_b.setStyleSheet("background-color: transparent;")
        hdr_b_lay = QVBoxLayout(hdr_b)
        hdr_b_lay.setContentsMargins(0, 0, 0, 0)
        hdr_b_lay.setSpacing(0)
        hdr_b_lay.addWidget(self.lbl_b_vol)
        hdr_b_lay.addWidget(self.val_b_vol)

        self.slider_b_vol = QSlider(Qt.Horizontal)
        self.slider_b_vol.setObjectName("slider_teal")
        self.slider_b_vol.setRange(0, 100)
        self.slider_b_vol.setValue(20)
        self.slider_b_vol.valueChanged.connect(
            lambda v: self.val_b_vol.setText(f"{v}%")
        )

        mixer_layout.addWidget(hdr_b)
        mixer_layout.addWidget(self.slider_b_vol)

        layout.addWidget(self.mixer_card)
        layout.addSpacing(12)

        # --- Load BGM Button (copper) ---
        self.btn_bgm = ShadowButton("Cargar Musica", color_class="copper")
        self.btn_bgm.clicked.connect(self.load_bgm_requested)
        layout.addWidget(self.btn_bgm)

        layout.addSpacing(10)

        self.btn_clear_cache = ShadowButton("Limpiar Cache", color_class="danger")
        self.btn_clear_cache.clicked.connect(self.clear_cache_requested)
        layout.addWidget(self.btn_clear_cache)

        layout.addSpacing(10)

        # --- Log toggle button (pill) ---
        self.btn_log_toggle = ShadowButton("Bitacora", color_class="copper_outline")
        self.btn_log_toggle.clicked.connect(self.log_toggle_requested)
        layout.addWidget(self.btn_log_toggle)

        # Push everything above; bottom buttons stay at bottom
        layout.addStretch()

    def _on_theme_clicked(self):
        """Emit theme mode based on current checkbox state.
        
        Uses clicked() signal (not stateChanged) so stylesheet reloads
        from _apply_theme don't trigger re-entrant state changes.
        """
        mode = "Dark" if self.theme_switch.isChecked() else "Light"
        self.theme_toggled.emit(mode)

    def update_history(self, paths):
        """Rebuild history buttons from a list of paths (max 5 shown, most recent first)."""
        while self.history_layout.count():
            item = self.history_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for path in paths[:5]:
            name = os.path.basename(path)
            if len(name) > 25:
                name = name[:22] + "..."
            btn = QPushButton(name)
            btn.setObjectName("btn_history")
            btn.clicked.connect(lambda checked, p=path: self.load_file_requested.emit(p))
            self.history_layout.addWidget(btn)

    def set_theme_mode(self, mode):
        """Set toggle state without emitting theme_toggled."""
        self.theme_switch.blockSignals(True)
        self.theme_switch.setChecked(mode == "Dark")
        self.theme_switch.blockSignals(False)

    def set_volume_values(self, voice_pct, music_pct):
        """Set slider values without triggering signals.
        
        Args:
            voice_pct: Voice volume as 0-100 integer (displayed as "N%").
                       Convert to float (÷100) before passing to VoiceSettings.volume
                       or the audio pipeline (FFmpeg expects 0.0-1.0).
            music_pct: BGM volume as 0-100 integer. Same ÷100 conversion needed
                       for AudioProject.bgm_volume / FFmpegAdapter bgm_vol.
        """
        self.slider_v_vol.blockSignals(True)
        self.slider_v_vol.setValue(voice_pct)
        self.slider_v_vol.blockSignals(False)
        self.val_v_vol.setText(f"{voice_pct}%")

        self.slider_b_vol.blockSignals(True)
        self.slider_b_vol.setValue(music_pct)
        self.slider_b_vol.blockSignals(False)
        self.val_b_vol.setText(f"{music_pct}%")
