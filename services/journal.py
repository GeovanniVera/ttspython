import tkinter as tk
from datetime import datetime

class Journal:
    def __init__(self, text_widget=None):
        self.text_widget = text_widget

    def set_widget(self, text_widget):
        self.text_widget = text_widget

    def log(self, message, level="INFO"):
        """
        Logs a message to the internal text widget if available.
        Format: [HH:MM:SS] [LEVEL] Message
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] [{level}] {message}\n"
        
        print(formatted_message.strip()) # Console fallback

        if self.text_widget:
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.insert(tk.END, formatted_message)
            self.text_widget.see(tk.END) # Scroll to bottom
            self.text_widget.config(state=tk.DISABLED)

    def error(self, message):
        self.log(message, "ERROR")

    def info(self, message):
        self.log(message, "INFO")
    
    def warning(self, message):
        self.log(message, "WARN")
