import sys
import os
from enum import Enum
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QPushButton
from PySide6.QtCore import Qt, Signal, QObject, QEvent
from PySide6.QtGui import QPalette, QColor, QPainter, QBrush

# --- 1. ENUMS ---
class GlassStyle(Enum):
    SIDEBAR = "sidebar"
    HEADER = "header"
    SHEET = "sheet"
    POPOVER = "popover"
    HUD = "hud"
    MENU = "menu"
    FULL = "underWindow"

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
        
        # Forzar repintado global
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
        if not app: return "light"
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

    def get_asset(self, filename):
        mode = self.get_current_mode()
        if mode == "light":
            return os.path.join(self._assets_path, filename)
        base, ext = os.path.splitext(filename)
        dark_name = f"{base}_dark{ext}"
        full_dark = os.path.join(self._assets_path, dark_name)
        if os.path.exists(full_dark): return full_dark
        return os.path.join(self._assets_path, filename)

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

# --- 3. WIDGET NATIVO INTELIGENTE ---
class NativeGlassWidget(QWidget):
    """
    Widget inteligente que adapta su renderizado según el SO y su jerarquía.
    - macOS: Siempre usa NSVisualEffectView nativo.
    - Windows TopLevel: Usa DWM Acrylic/Mica nativo.
    - Windows Child: Usa simulación de pintado (tinte) para evitar ghosting.
    """
    def __init__(self, style=GlassStyle.SIDEBAR, parent=None):
        super().__init__(parent)
        self._style = style
        self._border_radius = 0 # Default para llenar layouts
        GlassTheme.mode_changed.connect(self._on_mode_changed)
        
        # Base obligatoria: Transparencia en Qt para dejar ver el fondo
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")
        
        self._layout_proxy = None
        self._shield = None

        if sys.platform == "darwin":
            # --- MAC OS: SIEMPRE NATIVO ---
            # macOS soporta anidación perfecta, así que forzamos siempre lo nativo
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
            # --- WINDOWS: LÓGICA CONDICIONAL ---
            # No forzamos WA_NativeWindow aquí. Dejamos que Qt decida.
            # Si es ventana principal -> Qt lo hará nativo -> Activamos DWM.
            # Si es hijo -> Qt lo hará Alien -> Usamos pintado simulado.
            
            self.setAttribute(Qt.WA_NoSystemBackground, True)
            self._layout_proxy = QVBoxLayout(self)

        self._layout_proxy.setContentsMargins(0, 0, 0, 0)
        self._layout_proxy.setSpacing(0)

    # --- API PÚBLICA (Proxy al layout interno) ---
    def addWidget(self, widget, stretch=0, alignment=Qt.Alignment()):
        self._layout_proxy.addWidget(widget, stretch, alignment)

    def addLayout(self, layout, stretch=0):
        self._layout_proxy.addLayout(layout, stretch)

    def addStretch(self, stretch=0):
        self._layout_proxy.addStretch(stretch)
        
    def addSpacing(self, size):
        self._layout_proxy.addSpacing(size)
        
    def setRadius(self, radius):
        """Permite ajustar radio de borde en modo simulado (Windows Child)"""
        self._border_radius = radius
        self.update()

    def contentLayout(self):
        return self._layout_proxy

    # --- EVENTOS INTERNOS ---
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
        # Aplicar efecto nativo SOLO si es macOS o si es Ventana Principal en Windows
        if sys.platform == "darwin" or (sys.platform == "win32" and self.isWindow()):
            self._apply_native_effect()
            if sys.platform == "win32":
                self.window().repaint()

    def _on_mode_changed(self, mode):
        # Re-aplicar efecto al cambiar tema
        if sys.platform == "darwin" or (sys.platform == "win32" and self.isWindow()):
            self._apply_native_effect()
        self.update() # Forzar repintado para simulación Windows

    def paintEvent(self, event):
        if sys.platform == "win32":
            if self.isWindow():
                # Si es Ventana Principal: Limpiar fondo para ver Acrylic nativo
                painter = QPainter(self)
                painter.setCompositionMode(QPainter.CompositionMode_Clear)
                painter.fillRect(self.rect(), Qt.transparent)
            else:
                # Si es Hijo (Panel): Pintar simulación (Tinte)
                # Esto soluciona la duplicidad/ghosting
                self._paint_windows_simulation()
        else:
            super().paintEvent(event)

    def _paint_windows_simulation(self):
        """Dibuja el tinte semitransparente para hijos en Windows"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        mode = GlassTheme.get_current_mode()
        is_dark = (mode == "dark")
        
        # --- MATERIALES WINDOWS (ALPHAS AJUSTADOS PARA NOTORIEDAD) ---
        if self._style == GlassStyle.SIDEBAR:
            # Denso (80% opacidad)
            color = QColor(25, 25, 25, 200) if is_dark else QColor(245, 245, 245, 200)
        elif self._style == GlassStyle.POPOVER:
            # Muy transparente (20% opacidad) -> Se nota mucho el fondo
            color = QColor(40, 40, 40, 50) if is_dark else QColor(255, 255, 255, 50)
        elif self._style == GlassStyle.HEADER:
            # Medio (60% opacidad)
            color = QColor(30, 30, 30, 150) if is_dark else QColor(240, 240, 240, 150)
        elif self._style == GlassStyle.HUD:
            # Fantasma (10% opacidad)
            color = QColor(10, 10, 10, 30) if is_dark else QColor(255, 255, 255, 30)
        else:
            # Default
            color = QColor(30, 30, 30, 100) if is_dark else QColor(255, 255, 255, 100)

        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        # Usamos rect() completo para llenar el widget
        painter.drawRoundedRect(self.rect(), self._border_radius, self._border_radius)

    def _apply_native_effect(self):
        mode = GlassTheme.get_current_mode()
        apply_glass_logic(self, self._style, mode)

# --- IMPLEMENTACIÓN DE EFECTOS NATIVOS ---
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
        
        # Color base del Acrylic nativo (Ventana Principal)
        bg = "050505" if use_dark else "F2F2F2"
        # Alpha base: Qué tan transparente es la ventana contra el escritorio
        alpha = "CC" # 80% opacidad contra el escritorio
            
        color_hex = f"{alpha}{bg}"
        effect.setAcrylicEffect(oid, gradientColor=color_hex, isDarkMode=use_dark)

def apply_glass(target_object, style=GlassStyle.SIDEBAR, mode=None):
    """Helper para aplicar glass manualmente a una ventana existente (ej. Dialogs)"""
    if mode is None:
        mode = GlassTheme.get_current_mode()
    apply_glass_logic(target_object, style, mode)

class GlassButton(QPushButton):
    def __init__(self, text, color_role=None, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(34)
        self._color_role = color_role
        GlassTheme.mode_changed.connect(self._update_style)
        self._update_style()

    def _update_style(self, mode=None):
        if self._color_role:
            text_col = GlassTheme.get_color(self._color_role).name()
        else:
            text_col = "palette(text)"
        hover_col = GlassTheme.get_color("btn_hover").name()
        
        self.setStyleSheet(f"""
            QPushButton {{
                color: {text_col};
                background-color: transparent;
                border: none;
                border-radius: 6px;
                text-align: left;
                padding-left: 15px;
                font-size: 13px;
                font-family: '.AppleSystemUIFont', 'Segoe UI';
                opacity: 0.9;
            }}
            QPushButton:hover {{
                background-color: {hover_col};
                font-weight: 600;
            }}
        """)