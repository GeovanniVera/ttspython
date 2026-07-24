"""QPushButton with built-in drop shadow and pressed-state animation.

The style guide specifies:
  - border-radius: 0 (sharp corners)
  - box-shadow: 5px 5px 10px rgba(0,0,0,.18)
  - :active → translate(5px,5px) box-shadow:none (shadow disappears as button "sinks")

QSS doesn't support box-shadow, so we use QGraphicsDropShadowEffect.
On press, we zero the offset to simulate the button sinking into its shadow.
"""

from PySide6.QtWidgets import QPushButton, QGraphicsDropShadowEffect, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPalette, QIcon

from src.interfaces.gui.widgets.spinner_widget import SpinnerWidget


class ShadowButton(QPushButton):
    """QPushButton with drop shadow. Sharp corners (no border-radius in QSS)."""

    def __init__(self, text="", parent=None, color_class="copper"):
        """
        Args:
            color_class: "primary" (green), "danger" (red), or "copper" (default)
        """
        super().__init__(text, parent)
        self._color_class = color_class
        self._loading = False
        self._spinner = None
        self._saved_icon = QIcon()
        self._saved_text = ""

        # FIX #1: Prevent gradient leak from platform default palette.
        # Force Qt to paint via QSS only — no native style gradient underneath.
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(False)

        self._apply_color_class()

        # Drop shadow
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(10)
        self._shadow.setOffset(5, 5)
        self._shadow.setColor(QColor(0, 0, 0, 46))  # rgba(0,0,0,.18)
        self.setGraphicsEffect(self._shadow)

    def _apply_color_class(self):
        """Set QSS objectName for styling."""
        name_map = {
            "primary":         "btn_primary",
            "danger":          "btn_danger",
            "copper":          "btn_copper",
            "copper_outline":  "btn_copper_outline",
        }
        self.setObjectName(name_map.get(self._color_class, "btn_copper"))

    # ── Loading state (spinner + text swap) ───────────────────────────

    def set_loading(self, loading: bool, loading_text: str = ""):
        """Toggle loading spinner mode.

        When loading: saves the current icon, clears it, shows a rotating
        SpinnerWidget in its place, and swaps the button text to loading_text.
        Clicks are intercepted so the action can't fire twice.
        When done: restores icon, text, stops the spinner.
        """
        self._loading = loading
        if loading:
            self._saved_icon = QIcon(self.icon())
            self.setIcon(QIcon())
            self._saved_text = self.text()
            self.setText(loading_text)
            self._ensure_spinner()
            self._spinner.show()
            self._spinner.start()
            self._position_spinner()
        else:
            self.setIcon(self._saved_icon)
            self._saved_icon = QIcon()
            self.setText(self._saved_text)
            if self._spinner:
                self._spinner.stop()
                self._spinner.hide()

    def _ensure_spinner(self):
        if self._spinner is None:
            self._spinner = SpinnerWidget(parent=self, size=20)
        self._spinner.setFixedSize(20, 20)

    def _position_spinner(self):
        if self._spinner and self._spinner.isVisible():
            # Right side: after the text, same gap as the normal icon uses on the left
            x = self.width() - self._spinner.width() - 14
            y = (self.height() - self._spinner.height()) // 2
            self._spinner.move(max(14, x), max(0, y))

    def is_loading(self) -> bool:
        return self._loading

    def mousePressEvent(self, event):
        """Intercept clicks during loading; sink shadow on normal press."""
        if self._loading:
            event.ignore()
            return
        super().mousePressEvent(event)
        self._shadow.setOffset(1, 1)
        self._shadow.setBlurRadius(2)

    def mouseReleaseEvent(self, event):
        """Rise back from shadow on release."""
        if self._loading:
            return
        super().mouseReleaseEvent(event)
        self._shadow.setOffset(5, 5)
        self._shadow.setBlurRadius(10)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_spinner()

    def changeEvent(self, event):
        """FIX #5: Apply opacity effect when disabled (Qt QSS doesn't support opacity)."""
        if event.type() == event.Type.EnabledChange:
            if not self.isEnabled():
                # Swap to opacity effect (no shadow while disabled)
                self._opacity_effect = QGraphicsOpacityEffect(self)
                self._opacity_effect.setOpacity(0.4)
                self.setGraphicsEffect(self._opacity_effect)
            else:
                # Restore shadow effect
                self._shadow = QGraphicsDropShadowEffect(self)
                self._shadow.setBlurRadius(10)
                self._shadow.setOffset(5, 5)
                self._shadow.setColor(QColor(0, 0, 0, 46))
                self.setGraphicsEffect(self._shadow)
        super().changeEvent(event)
