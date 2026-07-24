import os
import platform
import subprocess
import sys
from pathlib import Path

class EnvManager:
    def __init__(self):
        # Detectar si estamos ejecutando desde un binario de PyInstaller
        if getattr(sys, 'frozen', False):
            # En el ejecutable, la raíz es la carpeta temporal de extracción (_MEIPASS)
            self.root = Path(sys._MEIPASS)
        else:
            # En desarrollo, la raíz es 3 niveles arriba de este archivo
            self.root = Path(__file__).resolve().parent.parent.parent
        
        # Definición de rutas relativas basadas en la búsqueda real
        self.tesseract_dir = self.root / "bin" / "tesseract"
        self.tesseract_exe = self.tesseract_dir / "tesseract.exe"
        self.tessdata_path = self.tesseract_dir / "tessdata"
        
        # Ruta corregida según el listado del sistema para Poppler
        self.poppler_bin = self.root / "bin" / "poppler" / "bin" / "Library" / "bin"

    def validate_binaries(self):
        """Verifica la existencia de los binarios críticos en la carpeta /bin."""
        checks = [
            (self.tesseract_exe, "Tesseract Executable"),
            (self.tessdata_path, "Tessdata Folder"),
            (self.poppler_bin / "pdftoppm.exe", "Poppler Binaries (pdftoppm)")
        ]
        
        missing = [name for path, name in checks if not path.exists()]
        
        if missing:
            print(f"\n[FATAL ERROR] Faltan componentes en la carpeta /bin:")
            for item in missing:
                print(f" - {item}")
            print(f"\nUbicación buscada: {self.root / 'bin'}")
            return False
        return True

    def setup_ocr_environment(self):
        """Configura las variables de entorno para pytesseract."""
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = str(self.tesseract_exe)
        os.environ['TESSDATA_PREFIX'] = str(self.tessdata_path)

    def get_poppler_path(self):
        return str(self.poppler_bin)

    def get_icon_path(self):
        """Devuelve la ruta al archivo de icono si existe."""
        icon_path = self.root / "app.ico"
        return str(icon_path) if icon_path.exists() else None

    def get_icon_path_for_platform(self):
        """Returns the appropriate icon path for the current platform."""
        import platform as _platform
        system = _platform.system()

        if system == "Windows":
            ico_path = self.root / "app.ico"
            return str(ico_path) if ico_path.exists() else None

        # Linux / macOS need PNG for iconphoto()
        png_path = self.root / "app.png"
        if not png_path.exists():
            ico_path = self.root / "app.ico"
            if ico_path.exists():
                try:
                    from PIL import Image
                    img = Image.open(str(ico_path))
                    img.save(str(png_path), "PNG")
                except Exception:
                    return None

        return str(png_path) if png_path.exists() else None


def open_path(path: str) -> None:
    """Opens a file or folder with the default system application."""
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(path)
        elif system == "Darwin":
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False)
    except FileNotFoundError:
        raise RuntimeError(
            f"No se encontró el explorador de archivos del sistema ({system}). "
            "Instale xdg-utils (Linux) o verifique la configuración."
        )


# Instancia única para todo el sistema
env_manager = EnvManager()
