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
    """
    def __init__(self, style=GlassStyle.SIDEBAR, mode="system", parent=None):
        super().__init__(parent)
        self._style = style
        self._mode = mode  # Guardamos la preferencia
        
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
        
        self.layout = QVBoxLayout(self._content_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def showEvent(self, event):
        super().showEvent(event)
        # Pasamos el modo al aplicar
        apply_glass(self, style=self._style, mode=self._mode)
    
    def addWidget(self, widget):
        self.layout.addWidget(widget)
        
    def addLayout(self, layout):
        self.layout.addLayout(layout)
        
    def setContentLayout(self, layout):
        QWidget().setLayout(self.layout)
        self.layout = layout
        self._content_widget.setLayout(layout)

# --- FUNCIÓN DE APLICACIÓN MAESTRA ---
def apply_glass(target_object, style=GlassStyle.SIDEBAR, mode="system"):
    """
    Aplica el efecto.
    mode: "system" (sigue al OS), "dark" (fuerza oscuro), "light" (fuerza claro)
    """
    oid = int(target_object.winId())

    # 1. Resolver si debe ser oscuro
    use_dark = False
    if mode == "dark":
        use_dark = True
    elif mode == "light":
        use_dark = False
    else:
        use_dark = is_dark_mode() # Detección automática

    if sys.platform == "darwin":
        is_window = target_object.isWindow() 
        if is_window:
            from .mac.window_effect import MacWindowEffect
            effect = MacWindowEffect(target_object)
            # Pasamos el 'mode' string explícito a Mac para que use setAppearance
            effect.set_mac_effect(oid, material_name=style.value, mode=mode)
        else:
            from .mac.widget_effect import MacWidgetEffect
            effect = MacWidgetEffect()
            # Los widgets heredan, pero podríamos forzar material
            effect.set_effect(oid, material_name=style.value)

    elif sys.platform == "win32":
        from .windows.window_effect import WindowsWindowEffect
        effect = WindowsWindowEffect(target_object)
        
        # --- MAPA DE TRADUCCIÓN MAC -> WINDOWS ---
        
        # Grupo 1: Superficies Base -> MICA (Standard)
        if style in [GlassStyle.SIDEBAR, GlassStyle.HEADER, GlassStyle.FULL]:
            effect.setMicaEffect(oid, isDarkMode=use_dark, isAlt=False)
            
        # Grupo 2: Superficies Secundarias -> MICA ALT (Tabbed)
        elif style in [GlassStyle.SHEET, GlassStyle.POPOVER]:
            effect.setMicaEffect(oid, isDarkMode=use_dark, isAlt=True)
            
        # Grupo 3: Superficies Flotantes -> ACRYLIC (Translucidez real)
        else: # HUD, MENU
            # Configuración personalizada de Acrylic para imitar HUD
            # Hex: AABBGGRR (Alpha, Blue, Green, Red) en memoria, o Hex String
            # Windows Acrylic Gradient Color: AABBGGRR en hex string
            if style == GlassStyle.HUD:
                # HUD es oscuro y muy transparente
                # Si forzamos Dark: Negro al 60% opacity -> 99000000 (aprox)
                # Si forzamos Light: Blanco al 60% -> 99FFFFFF
                color = "99101010" if use_dark else "99E0E0E0"
            else:
                # Menu estándar
                color = "CC202020" if use_dark else "CCF2F2F2"
                
            effect.setAcrylicEffect(oid, gradientColor=color, isDarkMode=use_dark)

# --- DETECTOR ---
def is_dark_mode(app_instance=None):
    if not app_instance:
        app_instance = QApplication.instance()
        if not app_instance:
            return False
            
    try:
        return app_instance.styleHints().colorScheme() == Qt.ColorScheme.Dark
    except Exception:
        try:
            text_color = app_instance.palette().color(QPalette.WindowText)
            return text_color.lightness() > 128
        except Exception:
            return False