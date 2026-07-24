"""Entry point — 100% Qt PySide6. Launches MainWindow."""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from src.interfaces.gui.main_window import MainWindow


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("PDF To Speech Studio")
    app.setApplicationVersion("4.1")

    ui_font = QFont("Inter", 13)
    ui_font.setStyleHint(QFont.SansSerif)
    app.setFont(ui_font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
