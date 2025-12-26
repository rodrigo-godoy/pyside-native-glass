import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QLabel, QFrame, 
                             QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QPropertyAnimation, QPoint, Property, QEasingCurve
from PySide6.QtGui import QColor, QPainter, QBrush, QPen

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
# Importamos GlassButton que acabamos de crear
from native_glass import apply_glass, GlassStyle, NativeGlassWidget, GlassTheme, GlassButton

# --- REGISTRO DE COLORES INTELIGENTES ---
# Definimos el color "danger" (Rojo).
# day: Rojo vibrante Apple. night: Rojo un poco más claro para contraste.
GlassTheme.register_color("danger", day="#FF3B30", night="#FF453A")

# --- SWITCH (ESTO ES UI ESPECÍFICA, SE QUEDA AQUÍ) ---
class ThemeSwitch(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 28)
        self.setCursor(Qt.PointingHandCursor)
        self._is_dark = True 
        self._thumb_x = 24.0
        self._anim = QPropertyAnimation(self, b"thumb_x", self)
        self._anim.setDuration(250)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def mouseReleaseEvent(self, event):
        self.toggle_mode()
        super().mouseReleaseEvent(event)

    def toggle_mode(self):
        self._is_dark = not self._is_dark
        mode = "dark" if self._is_dark else "light"
        GlassTheme.set_mode(mode)
        start = self._thumb_x
        end = 24.0 if self._is_dark else 4.0
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.start()

    def get_thumb_x(self): return self._thumb_x
    def set_thumb_x(self, x):
        self._thumb_x = x
        self.update()
    
    thumb_x = Property(float, get_thumb_x, set_thumb_x)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        track_col = QColor("#444") if self._is_dark else QColor("#CCC")
        thumb_col = QColor("white")
        p.setPen(Qt.NoPen)
        p.setBrush(track_col)
        p.drawRoundedRect(0, 0, self.width(), self.height(), 14, 14)
        if self._is_dark:
            p.setBrush(QColor(200, 200, 255))
            p.drawEllipse(10, 8, 10, 10)
            p.setBrush(track_col)
            p.drawEllipse(8, 6, 10, 10)
        else:
            p.setBrush(QColor(255, 180, 0))
            p.drawEllipse(30, 9, 10, 10)
        p.setBrush(thumb_col)
        p.drawEllipse(QPoint(int(self._thumb_x) + 11, 14), 11, 11)

# --- POPUP ---
class MaterialPopup(NativeGlassWidget):
    def __init__(self, style):
        super().__init__(style=style)
        self.resize(400, 300)
        self.setWindowTitle(f"Material: {style.value}")
        self.contentLayout().setAlignment(Qt.AlignCenter)
        
        lbl_name = QLabel(style.value)
        lbl_name.setStyleSheet("font-size: 32px; font-weight: 900; font-family: '.AppleSystemUIFont', 'Segoe UI'; border: none; color: palette(text);")
        self.addWidget(lbl_name)

# --- SIDEBAR ---
class SimpleSidebar(NativeGlassWidget):
    def __init__(self, main_window):
        super().__init__(style=GlassStyle.SIDEBAR)
        self.main_window = main_window
        self.setFixedWidth(240)
        
        self.contentLayout().setContentsMargins(16, 35, 16, 20)
        self.contentLayout().setSpacing(4)
        
        lbl_title = QLabel("MATERIALS")
        lbl_title.setStyleSheet("color: palette(text); font-weight: 900; font-size: 11px; margin-bottom: 8px; font-family: '.AppleSystemUIFont', 'Segoe UI'; border: none; letter-spacing: 1px;")
        self.addWidget(lbl_title)
        
        for style in GlassStyle:
            # USAMOS EL BOTÓN DE LA LIBRERÍA (Sin color_role = Automático B/N)
            btn = GlassButton(style.value)
            btn.clicked.connect(lambda checked=False, s=style: self.main_window.open_material_popup(s))
            self.addWidget(btn)
        
        self.contentLayout().addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        lbl_mode = QLabel("Appearance")
        lbl_mode.setStyleSheet("color: palette(text); opacity: 0.6; font-size: 11px; font-weight: 600; margin-bottom: 6px;")
        self.addWidget(lbl_mode)
        
        self.theme_switch = ThemeSwitch()
        self.addWidget(self.theme_switch, 0, Qt.AlignLeft)
        
        self.contentLayout().addSpacing(20)

        # BOTÓN SALIR CON ROL 'DANGER' (Aquí está la magia)
        btn_exit = GlassButton("Exit App", color_role="danger")
        btn_exit.clicked.connect(QApplication.instance().quit)
        self.addWidget(btn_exit)

# --- MAIN ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1100, 750)
        self.setWindowTitle("Native Glass App")
        self.active_popups = []
        
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        
        apply_glass(self, style=GlassStyle.SHEET)
        GlassTheme.mode_changed.connect(self.on_theme_changed)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.sidebar = SimpleSidebar(self)
        main_layout.addWidget(self.sidebar)
        
        content_area = QFrame()
        content_area.setObjectName("ContentArea")
        content_area.setStyleSheet("#ContentArea { border-left: 1px solid palette(mid); }")
        
        c_layout = QVBoxLayout(content_area)
        c_layout.setAlignment(Qt.AlignCenter)
        
        lbl_welcome = QLabel("Fully Automatic")
        lbl_welcome.setStyleSheet("color: palette(text); font-size: 60px; font-weight: 100; font-family: '.AppleSystemUIFont', 'Segoe UI'; border: none;")
        
        lbl_sub = QLabel("Color adapts seamlessly to your preference")
        lbl_sub.setStyleSheet("color: palette(button-text); opacity: 0.6; font-size: 20px; margin-top: 10px; font-family: '.AppleSystemUIFont', 'Segoe UI'; border: none;")
        
        c_layout.addWidget(lbl_welcome)
        c_layout.addWidget(lbl_sub)
        main_layout.addWidget(content_area)

    def on_theme_changed(self, mode):
        apply_glass(self, style=GlassStyle.SHEET)
        border_col = "#444" if mode == "dark" else "#CCC"
        self.findChild(QFrame, "ContentArea").setStyleSheet(f"#ContentArea {{ border-left: 1px solid {border_col}; }}")

    def open_material_popup(self, style):
        popup = MaterialPopup(style)
        popup.show()
        self.active_popups.append(popup)

    def closeEvent(self, event):
        for popup in self.active_popups:
            if popup.isVisible():
                popup.close()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = app.font()
    font.setFamily("Segoe UI")
    app.setFont(font)

    # Iniciar en Dark Mode
    GlassTheme.set_mode("dark")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())