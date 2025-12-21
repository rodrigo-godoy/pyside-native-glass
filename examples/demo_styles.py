import sys
import os
from PySide6.QtWidgets import (QApplication, QWidget, QGridLayout, 
                             QVBoxLayout, QLabel, QStackedLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette

# Setup path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from native_glass import apply_glass, GlassStyle

class GlassCanvas(QWidget):
    """
    EL LIENZO (VIDRIO). 
    Su única función es existir y tener el efecto nativo.
    Qt tiene prohibido pintar aquí.
    """
    def __init__(self, style):
        super().__init__()
        self.style = style
        # Se convierte en ventana nativa para recibir el cristal de macOS
        self.setAttribute(Qt.WA_NativeWindow)
        # Le prohibimos a Qt pintar el fondo (evita el cuadro gris)
        self.setAttribute(Qt.WA_NoSystemBackground)
        # Limpiamos la paleta por seguridad
        pal = self.palette()
        pal.setColor(QPalette.Window, Qt.transparent)
        self.setPalette(pal)
        
        # Borde sutil para ver dónde está el vidrio
        self.setStyleSheet("border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 12px;")

    def showEvent(self, event):
        super().showEvent(event)
        # Inyectamos el cristal
        apply_glass(self, style=self.style)

class ContentOverlay(QWidget):
    """
    LA CAPA DE DIBUJO (PLUMÓN).
    Es transparente y flota encima. Aquí van los widgets.
    """
    def __init__(self, title, subtitle):
        super().__init__()
        # Fondo transparente para ver el vidrio de abajo
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        lbl_name = QLabel(title)
        lbl_name.setAlignment(Qt.AlignCenter)
        lbl_name.setStyleSheet("""
            color: white; 
            font-weight: 900; 
            font-size: 26px; 
            font-family: '.AppleSystemUIFont';
        """)
        
        lbl_val = QLabel(subtitle)
        lbl_val.setAlignment(Qt.AlignCenter)
        lbl_val.setStyleSheet("color: #DDD; font-size: 14px;")
        
        layout.addWidget(lbl_name)
        layout.addWidget(lbl_val)

class FinalCorrectDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NATIVE GLASS: CANVAS & OVERLAY")
        self.resize(1200, 800)
        
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        
        # Fondo Global
        apply_glass(self, style=GlassStyle.HUD)

        grid = QGridLayout(self)
        grid.setSpacing(20)
        grid.setContentsMargins(30, 30, 30, 30)

        styles = list(GlassStyle)
        
        for index, style in enumerate(styles):
            row = index // 3
            col = index % 3
            
            # --- EL CONTENEDOR FÍSICO ---
            container = QWidget()
            container.setMinimumHeight(200)
            
            # Usamos QStackedLayout para poner uno ENCIMA del otro
            stack = QStackedLayout(container)
            stack.setStackingMode(QStackedLayout.StackAll)
            
            # 1. Ponemos el Vidrio (Fondo)
            canvas = GlassCanvas(style)
            stack.addWidget(canvas)
            
            # 2. Ponemos el Contenido (Frente)
            overlay = ContentOverlay(style.name, f"Material: {style.value}")
            stack.addWidget(overlay)
            
            grid.addWidget(container, row, col)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = FinalCorrectDemo()
    window.show()
    sys.exit(app.exec())