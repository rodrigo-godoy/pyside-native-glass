import sys
import os
from enum import Enum
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QPushButton
from PySide6.QtCore import Qt, Signal, QObject, QEvent
from PySide6.QtGui import QPalette, QColor, QPainter, QBrush

# --- 1. ENUMS ---
class GlassStyle(Enum):
    SIDEBAR = "sidebar"      # Fondo principal, más denso
    HEADER = "header"        # Barras superiores, transparencia media
    SHEET = "sheet"          # Diálogos modales
    POPOVER = "popover"      # Menús flotantes / Tarjetas, muy transparente
    HUD = "hud"              # Casi invisible
    MENU = "menu"            # Menús contextuales
    FULL = "underWindow"     # Fondo completo

# --- 2. MOTOR DE TEMAS ---
class ThemeManager(QObject):
    mode_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self._mode = "system"
        self._semantic_colors = {}
        self._assets_path = "assets"
        self.register_color("btn_hover", day="#E5E5E5", night="#3A3A3A")

    def set_assets_path(self, path):
        self._assets_path = path

    def set_mode(self, mode):
        self._mode = mode
        real_mode = self.get_current_mode()
        self._apply_qt_palette(real_mode)
        self.mode_changed.emit(real_mode)
        
        app = QApplication.instance()
        if app:
            for widget in app.topLevelWidgets():
                self._force_style_refresh(widget)

    def _force_style_refresh(self, widget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        for child in widget.findChildren(QWidget):
            child.style().unpolish(child)
            child.style().polish(child)
        widget.update()

    def get_current_mode(self):
        if self._mode in ["dark", "light"]:
            return self._mode
        app = QApplication.instance()
        if not app:
            return "light"
        try:
            return "dark" if app.styleHints().colorScheme() == Qt.ColorScheme.Dark else "light"
        except Exception:
            return "light"

    def register_color(self, name, day, night=None):
        if night is None:
            night = self._calculate_dark_variant(day)
        self._semantic_colors[name] = {"light": day, "dark": night}

    def get_color(self, name):
        mode = self.get_current_mode()
        if name in self._semantic_colors:
            return QColor(self._semantic_colors[name][mode])
        return QColor(name)

    def _calculate_dark_variant(self, hex_color):
        c = QColor(hex_color)
        h, s, lum = c.getHslF()
        new_lum = 1.0 - lum
        new_s = s * 0.8 if new_lum < 0.5 else s
        return QColor.fromHslF(h, new_s, new_lum).name()

    def _apply_qt_palette(self, mode):
        app = QApplication.instance()
        if not app: return
        palette = QPalette()
        if mode == "dark":
            base = QColor(30, 30, 30)
            text = QColor(255, 255, 255)
            palette.setColor(QPalette.WindowText, text)
            palette.setColor(QPalette.Text, text)
            palette.setColor(QPalette.ButtonText, text)
            palette.setColor(QPalette.Window, base)
            palette.setColor(QPalette.Base, base)
        else:
            base = QColor(255, 255, 255)
            text = QColor(0, 0, 0)
            palette.setColor(QPalette.WindowText, text)
            palette.setColor(QPalette.Text, text)
            palette.setColor(QPalette.ButtonText, text)
            palette.setColor(QPalette.Window, base)
            palette.setColor(QPalette.Base, base)
        app.setPalette(palette)

GlassTheme = ThemeManager()

# --- 3. WIDGET INTELIGENTE ---
class NativeGlassWidget(QWidget):
    def __init__(self, style=GlassStyle.SIDEBAR, parent=None):
        super().__init__(parent)
        self._style = style
        self._border_radius = 10 # Radio por defecto para simulaciones
        GlassTheme.mode_changed.connect(self._on_mode_changed)
        
        # Configuración base para transparencia en QT
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")
        
        # --- LÓGICA DE PLATAFORMA ---
        self._layout_proxy = None
        
        if sys.platform == "darwin":
            # macOS soporta anidación nativa perfecta
            self.setAttribute(Qt.WA_NativeWindow, True) 
            self.setAttribute(Qt.WA_NoSystemBackground, True)
            
            self._root_layout = QVBoxLayout(self)
            self._root_layout.setContentsMargins(0, 0, 0, 0)
            self._root_layout.setSpacing(0)
            
            self._shield = QWidget()
            self._shield.setAttribute(Qt.WA_NativeWindow, True)
            self._shield.setAttribute(Qt.WA_TranslucentBackground, True)
            self._shield.setStyleSheet("background: transparent;")
            
            self._root_layout.addWidget(self._shield)
            self._layout_proxy = QVBoxLayout(self._shield)
            
        elif sys.platform == "win32":
            # Windows NO soporta anidación de Acrylic/Mica sin ghosting.
            # ESTRATEGIA HÍBRIDA:
            # - Si es Ventana (TopLevel): Usa API Nativa (DWM).
            # - Si es Hijo (Child): Usa Simulación de Pintado (Qt Paint).
            
            self._is_toplevel = self.isWindow()
            
            if self._is_toplevel:
                self.setAttribute(Qt.WA_NoSystemBackground, True)
                # Solo activamos NativeWindow si somos ventana principal
                self.setAttribute(Qt.WA_NativeWindow, True) 
            else:
                # Si somos hijo, NO somos ventana nativa para evitar conflictos DWM
                self.setAttribute(Qt.WA_NativeWindow, False)
                
            self._shield = None
            self._layout_proxy = QVBoxLayout(self)

        self._layout_proxy.setContentsMargins(0, 0, 0, 0)
        self._layout_proxy.setSpacing(0)

    # --- API PÚBLICA (Simula layout normal) ---
    def addWidget(self, widget, stretch=0, alignment=Qt.Alignment()):
        self._layout_proxy.addWidget(widget, stretch, alignment)

    def addLayout(self, layout, stretch=0):
        self._layout_proxy.addLayout(layout, stretch)

    def addStretch(self, stretch=0):
        self._layout_proxy.addStretch(stretch)
        
    def addSpacing(self, size):
        self._layout_proxy.addSpacing(size)
        
    def setRadius(self, radius):
        """Permite ajustar el radio de borde para la simulación en Windows hijos"""
        self._border_radius = radius
        self.update()

    # --- INTERNOS ---
    def setLayout(self, layout):
        if sys.platform == "darwin":
            QWidget().setLayout(self._layout_proxy) 
            self._layout_proxy = layout
            self._shield.setLayout(layout)
        else:
            if self.layout():
                QWidget().setLayout(self.layout())
            super().setLayout(layout)
            self._layout_proxy = layout

    def showEvent(self, event):
        super().showEvent(event)
        # Aplicar efecto real solo si somos TopLevel en Windows o siempre en Mac
        if sys.platform == "darwin" or (sys.platform == "win32" and self.isWindow()):
            self._apply_effect()
            if sys.platform == "win32":
                self.window().repaint()

    def _on_mode_changed(self, mode):
        # Re-aplicar efecto nativo si corresponde
        if sys.platform == "darwin" or (sys.platform == "win32" and self.isWindow()):
            self._apply_effect()
        # Siempre repintar (para actualizar simulaciones de hijos)
        self.update()

    def paintEvent(self, event):
        # LÓGICA DE PINTADO HÍBRIDA
        if sys.platform == "win32":
            if self.isWindow():
                # Si es ventana principal, limpiar para dejar ver el Acrylic
                painter = QPainter(self)
                painter.setCompositionMode(QPainter.CompositionMode_Clear)
                painter.fillRect(self.rect(), Qt.transparent)
            else:
                # SI ES HIJO: SIMULAR MATERIAL
                # Esto arregla el "Fondo Negro" y la "Duplicidad"
                self._paint_windows_simulation()
        else:
            super().paintEvent(event)

    def _paint_windows_simulation(self):
        """Pinta un fondo semitransparente para simular capas de cristal en Windows hijos."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        mode = GlassTheme.get_current_mode()
        is_dark = (mode == "dark")
        
        # PALETA DE COLORES "HYPER-VIVID" PARA WINDOWS (Más notorios)
        # Ajustamos los alphas para que se note la diferencia de material
        if self._style == GlassStyle.SIDEBAR:
            # Sidebar: Oscuro/Claro denso pero visiblemente translúcido
            color = QColor(20, 20, 20, 180) if is_dark else QColor(245, 245, 245, 180)
        elif self._style == GlassStyle.POPOVER:
            # Popover: Muy transparente, efecto "flotante"
            color = QColor(45, 45, 45, 140) if is_dark else QColor(255, 255, 255, 140)
        elif self._style == GlassStyle.HEADER:
            color = QColor(30, 30, 30, 160) if is_dark else QColor(240, 240, 240, 160)
        elif self._style == GlassStyle.HUD:
            color = QColor(10, 10, 10, 80) if is_dark else QColor(255, 255, 255, 80)
        else:
            color = QColor(30, 30, 30, 200) if is_dark else QColor(255, 255, 255, 200)

        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        # Usamos un radio de borde para que se vea moderno
        painter.drawRoundedRect(self.rect(), self._border_radius, self._border_radius)

    def _apply_effect(self):
        mode = GlassTheme.get_current_mode()
        apply_glass_logic(self, self._style, mode)

# --- LÓGICA DE APLICACIÓN DE EFECTOS NATIVOS ---
def apply_glass_logic(target_object, style, mode):
    oid = int(target_object.winId())
    use_dark = (mode == "dark")

    if sys.platform == "darwin":
        is_window = target_object.isWindow() 
        if is_window:
            from .mac.window_effect import MacWindowEffect
            effect = MacWindowEffect(target_object)
            effect.set_mac_effect(oid, material_name=style.value, mode=mode)
        else:
            from .mac.widget_effect import MacWidgetEffect
            effect = MacWidgetEffect()
            effect.set_effect(oid, material_name=style.value, mode=mode)

    elif sys.platform == "win32":
        from .windows.window_effect import WindowsWindowEffect
        effect = WindowsWindowEffect(target_object)
        
        # CONFIGURACIÓN DE ALPHAS PARA WINDOWS 11 (VENTANA MADRE)
        # Aquí definimos qué tan transparente es la ventana principal
        # Hex AABBGGRR -> AA es Alpha.
        # Bajamos los alphas para hacer el efecto MÁS NOTORIO en el fondo.
        
        bg = "050505" if use_dark else "F0F0F0" # Color base casi negro/blanco
        
        # AJUSTES DE "NOTORIEDAD"
        if style in [GlassStyle.SIDEBAR, GlassStyle.FULL]:
            # Antes CC (80%), Ahora A0 (~60%) -> Más transparente
            alpha = "A0" if use_dark else "A0"
        elif style in [GlassStyle.HEADER, GlassStyle.SHEET]:
            alpha = "40" if use_dark else "70"
        elif style in [GlassStyle.MENU, GlassStyle.POPOVER]:
            alpha = "30" if use_dark else "50"
        elif style == GlassStyle.HUD:
            alpha = "10" # Muy fantasma
        else:
            alpha = "99"
            
        color_hex = f"{alpha}{bg}"
        # Usamos Acrylic (Blur) que es más bonito que Mica (Opaco)
        effect.setAcrylicEffect(oid, gradientColor=color_hex, isDarkMode=use_dark)

def apply_glass(target_object, style=GlassStyle.SIDEBAR, mode=None):
    """
    Helper function para aplicar manualmente glass a una ventana existente.
    Útil para diálogos QDialog estándar.
    """
    if mode is None:
        mode = GlassTheme.get_current_mode()
    apply_glass_logic(target_object, style, mode)