from datetime import datetime
import threading

class JournalAdapter:
    def __init__(self):
        self.callback = None
        self._lock = threading.Lock()

    def set_callback(self, callback):
        self.callback = callback

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] [{level}] {message}\n"
        
        # Thread-safe dispatch to callback
        if self.callback:
            with self._lock:
                self.callback(formatted_message)

    def error(self, message):
        self.log(message, "ERROR")

    def info(self, message):
        self.log(message, "INFO")
    
    def warning(self, message):
        self.log(message, "WARN")
