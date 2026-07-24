"""Toolbar widget: file load, destination, file name display, edit toggle."""

import os
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QCheckBox, QFrame, QSizePolicy
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Signal, QSize

from src.interfaces.gui.widgets.shadow_button import ShadowButton

# Icons directory
_ICONS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")


def _icon(name):
    """Load an SVG icon by name (without extension)."""
    path = os.path.join(_ICONS_DIR, f"{name}.svg")
    if os.path.exists(path):
        return QIcon(path)
    return QIcon()


def _enable_styled_background(widget):
    widget.setAttribute(Qt.WA_StyledBackground, True)


class Toolbar(QWidget):
    """Horizontal toolbar with load/destination buttons and edit toggle."""

    load_file_requested = Signal()
    select_destination_requested = Signal()
    edit_toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("toolbar")
        self.setFixedHeight(50)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        _enable_styled_background(self)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(8)

        # Load file button (copper, icon after label)
        self.btn_load = ShadowButton("Cargar Archivo", color_class="copper")
        self.btn_load.setIcon(_icon("upload"))
        self.btn_load.setIconSize(QSize(16, 16))
        self.btn_load.clicked.connect(self.load_file_requested)
        layout.addWidget(self.btn_load)

        # Destination button (copper)
        self.btn_dest = ShadowButton("Destino", color_class="copper")
        self.btn_dest.setIcon(_icon("folder"))
        self.btn_dest.setIconSize(QSize(16, 16))
        self.btn_dest.clicked.connect(self.select_destination_requested)
        layout.addWidget(self.btn_dest)

        # File name label
        self.lbl_file = QLabel("Arrastre un archivo aqui...")
        self.lbl_file.setObjectName("muted")
        layout.addWidget(self.lbl_file)

        layout.addStretch()

        # Edit mode toggle — same pill switch as Modo Oscuro
        self.switch_edit = QCheckBox("Edicion")
        self.switch_edit.setObjectName("switch_edit")
        self.switch_edit.setAutoFillBackground(False)
        self.switch_edit.setEnabled(False)
        self.switch_edit.clicked.connect(
            lambda: self.edit_toggled.emit(self.switch_edit.isChecked())
        )
        layout.addWidget(self.switch_edit)

    def set_file_label(self, name, loaded=True):
        """Update file name display."""
        self.lbl_file.setText(name)
        if loaded:
            self.lbl_file.setObjectName("file_name")
        else:
            self.lbl_file.setObjectName("muted")
        self.lbl_file.setStyleSheet("")  # force style refresh

    def set_edit_enabled(self, enabled):
        self.switch_edit.setEnabled(enabled)
