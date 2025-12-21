import sys
from enum import Enum
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette

class GlassStyle(Enum):
    SIDEBAR = "sidebar"
    HEADER = "header"
    SHEET = "sheet"
    POPOVER = "popover"
    HUD = "hud"
    MENU = "menu"
    FULL = "underWindow"

class NativeGlassWidget(QWidget):
    """
    EL WIDGET MÁGICO.
    Ya trae toda la arquitectura de 'Escudo' pre-configurada.
    """
    def __init__(self, style=GlassStyle.SIDEBAR, parent=None):
        super().__init__(parent)
        self._style = style
        
        # 1. Capa Fondo (Cristal)
        self.setAttribute(Qt.WA_NativeWindow)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        pal = self.palette()
        pal.setColor(QPalette.Window, Qt.transparent)
        self.setPalette(pal)

        # Layout del Padre
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        # 2. Capa Escudo (Contenido Seguro)
        self._content_widget = QWidget()
        self._content_widget.setAttribute(Qt.WA_NativeWindow)
        self._content_widget.setAttribute(Qt.WA_TranslucentBackground)
        self._content_widget.setStyleSheet("background: transparent;")
        
        self._main_layout.addWidget(self._content_widget)
        
        # Exponemos el layout interno
        self.layout = QVBoxLayout(self._content_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def showEvent(self, event):
        super().showEvent(event)
        apply_glass(self, style=self._style)
    
    def addWidget(self, widget):
        self.layout.addWidget(widget)
        
    def addLayout(self, layout):
        self.layout.addLayout(layout)
        
    def setContentLayout(self, layout):
        QWidget().setLayout(self.layout)
        self.layout = layout
        self._content_widget.setLayout(layout)

# --- FUNCIÓN DE APLICACIÓN ---
def apply_glass(target_object, style=GlassStyle.SIDEBAR, is_dark=True):
    oid = int(target_object.winId())

    if sys.platform == "darwin":
        is_window = target_object.isWindow() 
        if is_window:
            from .mac.window_effect import MacWindowEffect
            effect = MacWindowEffect(target_object)
            effect.set_mac_effect(oid, material_name=style.value)
        else:
            from .mac.widget_effect import MacWidgetEffect
            effect = MacWidgetEffect()
            effect.set_effect(oid, material_name=style.value)

    elif sys.platform == "win32":
        from .windows.window_effect import WindowsWindowEffect
        effect = WindowsWindowEffect(target_object)
        if style in [GlassStyle.SIDEBAR, GlassStyle.HEADER]:
            effect.setMicaEffect(oid, isDarkMode=is_dark, isAlt=False)
        else:
            color = "20202099" if is_dark else "F2F2F299"
            effect.setAcrylicEffect(oid, gradientColor=color)

# --- DETECTOR DE MODO OSCURO ---
def is_dark_mode(app_instance=None):
    if not app_instance:
        app_instance = QApplication.instance()
        if not app_instance:
            return False
            
    try:
        return app_instance.styleHints().colorScheme() == Qt.ColorScheme.Dark
    except Exception:
        # Fallback genérico seguro
        try:
            text_color = app_instance.palette().color(QPalette.WindowText)
            return text_color.lightness() > 128
        except Exception:
            return False