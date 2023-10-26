from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMessageBox


# Message box.
class CustomMessageBox(QMessageBox):
    def __init__(self, title, text):
        super().__init__()
        self.setWindowTitle(title)
        self.setText(text)
        font = QFont()
        font.setPointSize(14)
        self.setFont(font)
