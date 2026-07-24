"""Editor widget: text editor that toggles visibility."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QSizePolicy
from PySide6.QtCore import Qt, Signal


def _enable_styled_background(widget):
    widget.setAttribute(Qt.WA_StyledBackground, True)


class Editor(QWidget):
    """Toggleable text editor for extracted document text."""

    visibility_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("editor")
        _enable_styled_background(self)
        self.setVisible(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("El texto extraido del documento aparecera aqui...")
        self.text_edit.setAcceptRichText(False)
        self.text_edit.setMinimumHeight(200)
        self.text_edit.setMaximumHeight(400)
        layout.addWidget(self.text_edit)

    def set_content(self, text):
        """Replace editor content."""
        self.text_edit.setPlainText(text)

    def get_content(self):
        """Return editor content."""
        return self.text_edit.toPlainText()

    def toggle_visibility(self):
        """Show/hide the editor."""
        self.setVisible(not self.isVisible())
        self.visibility_changed.emit(self.isVisible())

    def show_editor(self):
        self.setVisible(True)
        self.visibility_changed.emit(True)

    def hide_editor(self):
        self.setVisible(False)
        self.visibility_changed.emit(False)
