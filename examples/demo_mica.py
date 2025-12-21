import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

# Setup path to find your local library
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from native_glass import apply_mica

class GlassWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(600, 400)
        self.setWindowTitle("PySide6 Native Glass Demo")
        
        # 1. Essential for macOS/Windows transparency
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 2. Apply the effect
        apply_mica(self)
        
        # UI Elements
        layout = QVBoxLayout(self)
        # We use a semi-transparent dark background for the label 
        # so it's readable over any wallpaper
        self.label = QLabel("✨ Native Glass Effect ✨\n(Running on macOS)")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                font-size: 24px; 
                color: white; 
                font-weight: bold;
                background-color: rgba(0, 0, 0, 50);
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GlassWindow()
    window.show()
    sys.exit(app.exec())