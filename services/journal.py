import tkinter as tk
from datetime import datetime

class Journal:
    def __init__(self, text_widget=None):
        self.text_widget = text_widget
        self.callback = None

    def set_widget(self, text_widget):
        self.text_widget = text_widget

    def set_callback(self, callback):
        """Sets a callback function to handle log messages (useful for thread-safety)."""
        self.callback = callback

    def log(self, message, level="INFO"):
        """
        Logs a message to the internal text widget/callback if available.
        Format: [HH:MM:SS] [LEVEL] Message
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] [{level}] {message}\n"
        
        print(formatted_message.strip()) # Console fallback

        if self.callback:
            self.callback(formatted_message)
        elif self.text_widget:
            try:
                self.text_widget.configure(state="normal")
                self.text_widget.insert("end", formatted_message)
                self.text_widget.see("end") 
                self.text_widget.configure(state="disabled")
            except Exception as e:
                print(f"Journal Error: {e}")

    def error(self, message):
        self.log(message, "ERROR")

    def info(self, message):
        self.log(message, "INFO")
    
    def warning(self, message):
        self.log(message, "WARN")
