import os
import sys
from tkinter import messagebox
import tkinter as tk

# Asegurar que el root esté en el path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.infrastructure.env_manager import env_manager
from src.interfaces.gui.app import AntigravityApp

if __name__ == "__main__":
    # VALIDACIÓN INICIAL DE BINARIOS LOCALES
    if not env_manager.validate_binaries():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Error de Sistema", 
            "No se encontraron los binarios de Tesseract o Poppler en la carpeta /bin.\n\n"
            "La aplicación no puede continuar."
        )
        sys.exit(1)

    # Lanzar Aplicación
    app = AntigravityApp()
    app.mainloop()
