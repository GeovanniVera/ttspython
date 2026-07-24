"""Action panel widget: voice controls and process buttons."""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QComboBox,
    QSlider, QLabel, QPushButton, QSizePolicy
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal, Qt, QSize

from src.interfaces.gui.widgets.shadow_button import ShadowButton

_ICONS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")


def _icon(name):
    path = os.path.join(_ICONS_DIR, f"{name}.svg")
    if os.path.exists(path):
        return QIcon(path)
    return QIcon()


def _enable_styled_background(widget):
    widget.setAttribute(Qt.WA_StyledBackground, True)


class ActionPanel(QWidget):
    """Voice controls (voice, rate, pitch) and process buttons (start, stop, preview)."""

    preview_requested = Signal()
    start_requested = Signal()
    stop_requested = Signal()

    VOICES = [
        "es-MX-JorgeNeural",
        "es-CL-LorenzoNeural",
        "es-MX-DaliaNeural",
        "es-ES-AlvaroNeural",
        "en-US-GuyNeural",
        "en-US-AvaNeural",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("action_panel")
        _enable_styled_background(self)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        card = QFrame()
        card.setObjectName("action_panel_card")
        _enable_styled_background(card)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # ── Voice row ──
        vrow = QHBoxLayout()
        vrow.setSpacing(16)

        # Voice selector
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(self.VOICES)
        self.voice_combo.setCurrentIndex(0)
        self.voice_combo.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        vrow.addWidget(self.voice_combo)

        # Separator
        vrow.addSpacing(8)

        # Rate group: label + value + slider
        rate_group = QWidget()
        rate_group.setAutoFillBackground(False)
        rate_group.setStyleSheet("background-color: transparent;")
        rate_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        rate_lay = QVBoxLayout(rate_group)
        rate_lay.setContentsMargins(0, 0, 0, 0)
        rate_lay.setSpacing(4)

        rate_header = QWidget()
        rate_header.setAutoFillBackground(False)
        rate_header.setStyleSheet("background-color: transparent;")
        rate_header_lay = QHBoxLayout(rate_header)
        rate_header_lay.setContentsMargins(0, 0, 0, 0)
        rate_header_lay.setSpacing(8)
        self.lbl_rate = QLabel("Velo")
        self.lbl_rate.setObjectName("mixer_label")
        self.val_rate = QLabel("+0%")
        self.val_rate.setObjectName("mixer_value")
        rate_header_lay.addWidget(self.lbl_rate)
        rate_header_lay.addStretch()
        rate_header_lay.addWidget(self.val_rate)

        self.slider_rate = QSlider(Qt.Horizontal)
        self.slider_rate.setObjectName("slider_copper")
        self.slider_rate.setRange(-50, 50)
        self.slider_rate.setValue(0)
        self.slider_rate.setMinimumWidth(120)
        self.slider_rate.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.slider_rate.valueChanged.connect(
            lambda v: self.val_rate.setText(f"{v:+d}%")
        )

        rate_lay.addWidget(rate_header)
        rate_lay.addWidget(self.slider_rate)
        vrow.addWidget(rate_group, stretch=2)

        # Pitch group: label + value + slider
        pitch_group = QWidget()
        pitch_group.setAutoFillBackground(False)
        pitch_group.setStyleSheet("background-color: transparent;")
        pitch_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        pitch_lay = QVBoxLayout(pitch_group)
        pitch_lay.setContentsMargins(0, 0, 0, 0)
        pitch_lay.setSpacing(4)

        pitch_header = QWidget()
        pitch_header.setAutoFillBackground(False)
        pitch_header.setStyleSheet("background-color: transparent;")
        pitch_header_lay = QHBoxLayout(pitch_header)
        pitch_header_lay.setContentsMargins(0, 0, 0, 0)
        pitch_header_lay.setSpacing(8)
        self.lbl_pitch = QLabel("Tono")
        self.lbl_pitch.setObjectName("mixer_label")
        self.val_pitch = QLabel("+0Hz")
        self.val_pitch.setObjectName("mixer_value")
        pitch_header_lay.addWidget(self.lbl_pitch)
        pitch_header_lay.addStretch()
        pitch_header_lay.addWidget(self.val_pitch)

        self.slider_pitch = QSlider(Qt.Horizontal)
        self.slider_pitch.setObjectName("slider_copper")
        self.slider_pitch.setRange(-20, 20)
        self.slider_pitch.setValue(0)
        self.slider_pitch.setMinimumWidth(120)
        self.slider_pitch.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.slider_pitch.valueChanged.connect(
            lambda v: self.val_pitch.setText(f"{v:+d}Hz")
        )

        pitch_lay.addWidget(pitch_header)
        pitch_lay.addWidget(self.slider_pitch)
        vrow.addWidget(pitch_group, stretch=2)

        # Preview button
        self.btn_preview = ShadowButton("Escuchar", color_class="copper")
        self.btn_preview.setIcon(_icon("headphones"))
        self.btn_preview.setIconSize(QSize(16, 16))
        self.btn_preview.setMinimumWidth(130)
        self.btn_preview.clicked.connect(self.preview_requested)
        vrow.addWidget(self.btn_preview, alignment=Qt.AlignBottom)

        layout.addLayout(vrow)

        # ── Process row ──
        arow = QHBoxLayout()
        arow.setSpacing(16)

        self.btn_process = ShadowButton("Iniciar Proceso", color_class="primary")
        self.btn_process.setIcon(_icon("play"))
        self.btn_process.setIconSize(QSize(16, 16))
        self.btn_process.setMinimumHeight(52)
        self.btn_process.clicked.connect(self.start_requested)
        arow.addWidget(self.btn_process, stretch=1)

        self.btn_cancel = ShadowButton("Detener", color_class="danger")
        self.btn_cancel.setIcon(_icon("stop"))
        self.btn_cancel.setIconSize(QSize(16, 16))
        self.btn_cancel.setFixedHeight(52)
        self.btn_cancel.setMinimumWidth(160)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.stop_requested)
        arow.addWidget(self.btn_cancel)

        layout.addLayout(arow)

        outer.addWidget(card)

    def get_voice(self):
        return self.voice_combo.currentText()

    def get_rate(self):
        return self.slider_rate.value()

    def get_pitch(self):
        return self.slider_pitch.value()

    def set_voice(self, voice_id):
        idx = self.voice_combo.findText(voice_id)
        if idx >= 0:
            self.voice_combo.setCurrentIndex(idx)

    def set_process_loading(self, loading: bool):
        """Toggle spinner on 'Iniciar Proceso' button while pipeline runs."""
        self.btn_process.set_loading(loading, loading_text="Procesando...")
        self.set_cancel_enabled(loading)

    def set_preview_loading(self, loading: bool):
        """Toggle spinner on 'Escuchar' button while preview generates."""
        self.btn_preview.set_loading(loading, loading_text="Generando...")

    def set_actions_enabled(self, enabled: bool):
        """Enable/disable process and preview buttons based on text availability."""
        self.btn_process.setEnabled(enabled)
        self.btn_preview.setEnabled(enabled)

    def set_process_text(self, text):
        self.btn_process.setText(text)

    def set_cancel_enabled(self, enabled):
        self.btn_cancel.setEnabled(enabled)
