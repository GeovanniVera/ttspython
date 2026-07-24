"""Log console widget: colored log output with show/hide toggle.

Style guide section 07 specifies:
  - Console background: always dark (#12141A) regardless of theme
  - Font: JetBrains Mono 12.5px, line-height 1.9
  - Level colors:
    - [INFO]  → #5AA9E6 (blue)
    - [WARN]  → #D98A3D (signal-amber)
    - [ERROR] → #EF6E63 (soft red)
    - [OK]    → #3FAE6A (signal-green)
    - timestamp → #6B7280 (muted gray)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QTextEdit, QLabel,
    QPushButton, QSizePolicy, QStackedWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QTextCharFormat, QFont, QTextCursor

# Style-guide log level colors (section 07)
LOG_COLORS = {
    "INFO":  QColor("#5AA9E6"),
    "WARN":  QColor("#D98A3D"),
    "ERROR": QColor("#EF6E63"),
    "OK":    QColor("#3FAE6A"),
}

DEFAULT_COLOR = QColor("#ECEAE4")


def _enable_styled_background(widget):
    widget.setAttribute(Qt.WA_StyledBackground, True)


class LogConsole(QWidget):
    """Collapsible log panel with colored text by level."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("log_container")
        _enable_styled_background(self)
        self._visible = False
        self.setVisible(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header (top half of unified container) ──
        header = QFrame()
        header.setObjectName("log_header")
        _enable_styled_background(header)
        header.setFixedHeight(30)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 0, 10, 0)

        title = QLabel("BITÁCORA")
        title.setObjectName("section")
        header_layout.addWidget(title)
        header_layout.addStretch()

        btn_close = QPushButton("X")
        btn_close.setObjectName("btn_flat")
        btn_close.setFixedSize(30, 25)
        btn_close.clicked.connect(self.hide_console)
        header_layout.addWidget(btn_close)

        layout.addWidget(header)

        # ── Body area (bottom half of unified container) ──
        body = QFrame()
        body.setObjectName("log_body")
        _enable_styled_background(body)
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Empty-state placeholder — shown until first real log
        self.empty_label = QLabel("Los registros del proceso aparecerán aquí")
        self.empty_label.setObjectName("log_empty")
        self.empty_label.setAlignment(Qt.AlignCenter)

        # Log text area — monospace, dark bg
        self.text_edit = QTextEdit()
        self.text_edit.setObjectName("log_console")
        self.text_edit.setReadOnly(True)
        self.text_edit.setMinimumHeight(150)
        self.text_edit.setMaximumHeight(250)

        # Font handled entirely by QSS (QTextEdit#log_console).
        # No setFont() here — it would prevent QSS font-size/family from applying.

        # Stacked widget toggles between empty-state label and live log area
        self.stack = QStackedWidget()
        self.stack.setObjectName("log_stack")
        self.stack.addWidget(self.empty_label)   # index 0
        self.stack.addWidget(self.text_edit)     # index 1
        self.stack.setCurrentIndex(0)

        body_layout.addWidget(self.stack)
        layout.addWidget(body, stretch=1)

        # Bitácora starts empty — logs appear only from real events.

    def show_console(self):
        self._visible = True
        self.setVisible(True)

    def hide_console(self):
        self._visible = False
        self.setVisible(False)

    def toggle_console(self):
        if self._visible:
            self.hide_console()
        else:
            self.show_console()

    def append(self, message):
        """Append a log line, auto-detecting level from [LEVEL] tags.

        Handles messages both with and without trailing newline (JournalAdapter
        includes one internally; direct calls usually don't).
        """
        # Switch from empty-state to live log view on first append
        if self.stack.currentIndex() == 0:
            self.stack.setCurrentIndex(1)

        # Normalise trailing newline (accept both "msg\\n" and "msg")
        message = message.rstrip("\n")

        level = "INFO"
        for tag in LOG_COLORS:
            if f"[{tag}]" in message:
                level = tag
                break

        fmt = QTextCharFormat()
        fmt.setForeground(LOG_COLORS.get(level, DEFAULT_COLOR))

        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(message + "\n", fmt)

        scrollbar = self.text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear(self):
        self.text_edit.clear()
        self.stack.setCurrentIndex(0)
