"""Rotating spinner widget — animated SVG arc for loading states.

Paints the spinner SVG rotated by a QPropertyAnimation-driven angle,
matching the icon style guide (stroke-based, stroke-width: 2,
stroke-linecap: round, no fill). One full rotation ≈ 900ms.
"""

import os
from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Qt, QPropertyAnimation, Property, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QFont


_ICONS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")


class SpinnerWidget(QWidget):
    """Fixed-size widget that renders a continuously rotating spinner arc.

    Usage:
        spinner = SpinnerWidget()
        spinner.start()  # begins rotation animation
        spinner.stop()   # stops and resets to 0°
    """

    ROTATION_DURATION = 900  # ms per full turn

    def __init__(self, parent=None, size=20):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self._angle = 0.0
        self._stroke_color = QColor("#ECEAE4")  # default text-light

        # ── Animation ──
        self._animation = QPropertyAnimation(self, b"angle", self)
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(360.0)
        self._animation.setDuration(self.ROTATION_DURATION)
        self._animation.setLoopCount(-1)

    # ── Public API ───────────────────────────────────────────────────

    def start(self):
        """Begin the rotation animation loop."""
        if self._animation.state() != QPropertyAnimation.State.Running:
            self._animation.start()

    def stop(self):
        """Stop the animation and reset to 0°."""
        self._animation.stop()
        self._angle = 0.0
        self.update()

    def set_stroke_color(self, color: QColor):
        """Override the spinner stroke color (e.g. to match theme)."""
        self._stroke_color = color
        self.update()

    # ── Angle property (for QPropertyAnimation) ──────────────────────

    def _get_angle(self) -> float:
        return self._angle

    def _set_angle(self, val: float):
        self._angle = val
        self.update()

    angle = Property(float, _get_angle, _set_angle)

    # ── Paint ────────────────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        s = self.width()
        center = s / 2.0
        radius = center - 2  # 2px inset for stroke-width margin

        painter.translate(center, center)
        painter.rotate(self._angle)
        painter.translate(-center, -center)

        pen = QPen(self._stroke_color, 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # 270° arc: from top (12 o'clock) clockwise to ~4:30 position
        # Arc in a bounding rect, startAngle=90° (Qt: 0=3 o'clock, 90=12 o'clock)
        # spanAngle=270° * 16 (Qt uses 1/16 degree units)
        rect = QRectF(center - radius, center - radius, radius * 2, radius * 2)
        painter.drawArc(rect, 90 * 16, 270 * 16)

        painter.end()
