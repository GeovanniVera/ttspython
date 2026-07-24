"""Progress area: EqualizerMeter + status label."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt

from src.interfaces.gui.widgets.equalizer_meter import EqualizerMeter


def _enable_styled_background(widget):
    widget.setAttribute(Qt.WA_StyledBackground, True)


class ProgressBar(QWidget):
    """Equalizer-meter progress bar with status text underneath."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("progress_area")
        _enable_styled_background(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 4)
        layout.setSpacing(6)

        self.meter = EqualizerMeter()
        layout.addWidget(self.meter)

        self.lbl_status = QLabel("Listo")
        self.lbl_status.setObjectName("status")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_status)

    def set_progress(self, value_0_1):
        """Set progress as float 0.0 - 1.0."""
        self.meter.set_progress(value_0_1)

    def set_status(self, text):
        self.lbl_status.setText(text)

    def reset(self):
        self.meter.reset()
        self.lbl_status.setText("Listo")
