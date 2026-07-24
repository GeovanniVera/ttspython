"""Equalizer-style progress meter — signature element of the Studio UI.

Renders 36 narrow vertical bars that fill left-to-right as chunks are
processed. Active bars use a copper-to-green gradient; inactive bars use
border-soft. Container is bg_card, border, r-sm (6px), 38px tall.
"""

import math

from PySide6.QtWidgets import QWidget, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Qt, Property
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QBrush


class MeterBar(QWidget):
    """Single bar in the equalizer meter. Paints itself with gradient or inactive color."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._active = False
        self._bar_height = 0.25  # 0.0 - 1.0 for animation
        self._target_height = 0.25
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(False)
        # Inline beats generic QWidget bg in the cascade
        self.setStyleSheet("background-color: transparent;")
        self.setFixedWidth(5)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

    def set_active(self, active):
        self._active = active
        self.update()

    def set_bar_height(self, h):
        self._bar_height = h
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        gap = 1  # px gap at bottom for visual breathing room

        if self._active:
            # Copper-to-green gradient
            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0, QColor("#EFAD82"))    # copper-300
            grad.setColorAt(1, QColor("#3FAE6A"))    # signal-green
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.NoPen)

            bar_h = max(4, int((h - gap) * self._bar_height))
            bar_y = h - gap - bar_h  # anchored to bottom
            painter.drawRoundedRect(1, bar_y, w - 2, bar_h, 1, 1)
        else:
            # Inactive: border-soft color, thin bar anchored to bottom
            painter.setBrush(QColor("#454C61"))
            painter.setPen(Qt.NoPen)
            bar_h = max(4, int((h - gap) * 0.2))
            bar_y = h - gap - bar_h  # anchored to bottom
            painter.drawRoundedRect(1, bar_y, w - 2, bar_h, 1, 1)

        painter.end()


class EqualizerMeter(QWidget):
    """36-bar equalizer progress meter.

    Usage:
        meter = EqualizerMeter()
        meter.set_progress(0.65)  # 0.0 - 1.0, fills bars left-to-right
    """

    BAR_COUNT = 36

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("equalizer_meter")
        self.setFixedHeight(38)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self._progress = 0.0
        self._bars = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(1)
        layout.setAlignment(Qt.AlignCenter)

        for i in range(self.BAR_COUNT):
            bar = MeterBar()
            self._bars.append(bar)
            layout.addWidget(bar)

        self._update_bars()

    def _get_progress(self):
        return self._progress

    def _set_progress(self, value):
        self._progress = max(0.0, min(1.0, value))
        self._update_bars()

    progress = Property(float, _get_progress, _set_progress)

    def set_progress(self, value):
        """Set progress as float 0.0 - 1.0."""
        self._set_progress(value)

    def _update_bars(self):
        active_count = int(self._progress * self.BAR_COUNT)
        for i, bar in enumerate(self._bars):
            is_active = i < active_count
            bar.set_active(is_active)
            if is_active:
                h = 0.3 + abs(math.sin(i * 1.2)) * 0.55
                bar.set_bar_height(h)
            else:
                bar.set_bar_height(0.2)

    def reset(self):
        self._set_progress(0.0)
