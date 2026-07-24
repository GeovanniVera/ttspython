"""Qt signals and bridges for thread-safe communication.

Defined here for phases 3-4. Phase 1 only uses the window layout.
"""

from PySide6.QtCore import QObject, Signal


class WorkerSignals(QObject):
    """Signals emitted by background worker threads."""

    progress = Signal(str, float)       # (message, progress_value 0.0-1.0)
    finished = Signal(str)              # final mp3 path
    error = Signal(str)                 # error message
    extraction_complete = Signal(str)   # extracted text


class QtJournalBridge(QObject):
    """Bridges JournalAdapter callbacks to Qt signals.

    When connected, JournalAdapter.formatted_message() emits a Signal
    that Qt delivers on the main thread — no polling, no queue.
    """

    message_received = Signal(str)

    def __init__(self, journal, parent=None):
        super().__init__(parent)
        self._journal = journal
        self._journal.set_callback(self._on_message)

    def _on_message(self, formatted_message: str):
        self.message_received.emit(formatted_message)
