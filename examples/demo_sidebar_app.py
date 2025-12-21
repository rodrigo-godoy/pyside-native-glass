import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QLabel, QFrame, 
                             QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from native_glass import apply_glass, GlassStyle, NativeGlassWidget

# --- POP-UP DEMO ---
class MaterialPopup(NativeGlassWidget):
    def __init__(self, style):
        super().__init__(style=style)
        self.resize(400, 300)
        self.setWindowTitle(f"Material: {style.value}")
        self.layout.setAlignment(Qt.AlignCenter)
        
        lbl_name = QLabel(style.value)
        # USAMOS palette(text) -> El color nativo del sistema
        lbl_name.setStyleSheet("font-size: 32px; font-weight: 900; font-family: '.AppleSystemUIFont'; border: none; color: palette(text);")
        self.addWidget(lbl_name)

class MenuButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(34)
        # CSS INTELIGENTE:
        # color: palette(text) -> Se adapta solo a negro o blanco
        self.setStyleSheet("""
            QPushButton {
                color: palette(text); 
                background-color: transparent;
                border: none;
                border-radius: 6px;
                text-align: left;
                padding-left: 15px;
                font-size: 13px;
                font-family: '.AppleSystemUIFont';
                opacity: 0.8;
            }
            QPushButton:hover { 
                background-color: palette(highlight); 
                color: palette(highlighted-text);
            }
        """)

# --- SIDEBAR (Material SIDEBAR en lugar de HUD) ---
class SimpleSidebar(NativeGlassWidget):
    def __init__(self, main_window):
        # CAMBIO: Usamos SIDEBAR, que cambia de color claro/oscuro automáticamente
        super().__init__(style=GlassStyle.SIDEBAR)
        self.main_window = main_window
        self.setFixedWidth(240)
        
        self.layout.setContentsMargins(16, 35, 16, 20)
        self.layout.setSpacing(4)
        
        lbl_title = QLabel("materiales")
        # Usamos palette(mid) para un color de subtítulo nativo
        lbl_title.setStyleSheet("color: palette(link-visited); font-weight: 700; font-size: 11px; margin-bottom: 8px; font-family: '.AppleSystemUIFont'; border: none;")
        self.addWidget(lbl_title)
        
        for style in GlassStyle:
            btn = MenuButton(style.value)
            btn.clicked.connect(lambda checked=False, s=style: self.main_window.open_material_popup(s))
            self.addWidget(btn)
        
        self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        btn_exit = MenuButton("salir")
        btn_exit.setStyleSheet("color: #ff6b6b; font-weight: bold; text-align: left; padding-left: 15px; border: none;")
        btn_exit.clicked.connect(QApplication.instance().quit)
        self.addWidget(btn_exit)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1100, 750)
        self.setWindowTitle("App Nativa Lista")
        self.active_popups = []
        
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        apply_glass(self, style=GlassStyle.SHEET) 
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.sidebar = SimpleSidebar(self)
        main_layout.addWidget(self.sidebar)
        
        content_area = QFrame()
        content_area.setObjectName("ContentArea")
        # Borde semitransparente basado en el color del texto
        content_area.setStyleSheet("#ContentArea { border-left: 1px solid palette(midlight); }")
        
        c_layout = QVBoxLayout(content_area)
        c_layout.setAlignment(Qt.AlignCenter)
        
        lbl_welcome = QLabel("Todo Automático")
        # EL GRAN CAMBIO: palette(text)
        lbl_welcome.setStyleSheet("color: palette(text); font-size: 60px; font-weight: 100; font-family: '.AppleSystemUIFont'; border: none;")
        
        lbl_sub = QLabel("El color se adapta al sistema sin código extra")
        lbl_sub.setStyleSheet("color: palette(button-text); opacity: 0.6; font-size: 20px; margin-top: 10px; font-family: '.AppleSystemUIFont'; border: none;")
        
        c_layout.addWidget(lbl_welcome)
        c_layout.addWidget(lbl_sub)
        
        main_layout.addWidget(content_area)

    def open_material_popup(self, style):
        popup = MaterialPopup(style)
        popup.show()
        self.active_popups.append(popup)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())