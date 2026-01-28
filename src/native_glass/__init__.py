import sys
import os
import ctypes
from ctypes import c_int, byref, sizeof, Structure
from enum import Enum
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QPushButton
from PySide6.QtCore import Qt, Signal, QObject, QEvent
from PySide6.QtGui import QPalette, QColor, QPainter, QBrush, QPen

# --- 1. API DWM WINDOWS (Directa, sin archivos extra) ---
if sys.platform == "win32":
    dwmapi = ctypes.windll.dwmapi
    
    class MARGINS(Structure):
        _fields_ = [("cxLeftWidth", c_int), ("cxRightWidth", c_int),
                    ("cyTopHeight", c_int), ("cyBottomHeight", c_int)]

    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    DWMWA_SYSTEMBACKDROP_TYPE = 38
    
    # Usamos Acrylic (3) porque confirmaste que es el único que NO se ve negro
    DWMSBT_TRANSIENTWINDOW = 3 

# --- 2. ENUMS ---
class GlassStyle(Enum):
    SIDEBAR = "sidebar"
    HEADER = "header"
    SHEET = "sheet"
    POPOVER = "popover"
    HUD = "hud"
    MENU = "menu"
    FULL = "underWindow"

# --- 3. MOTOR DE TEMAS ---
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
        self._real_mode = self.get_current_mode()
        self._apply_qt_palette(self._real_mode)
        self.mode_changed.emit(self._real_mode)
        
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
        # IMPORTANTE: Base transparente global
        base = QColor(0, 0, 0, 0)
        text = QColor(255, 255, 255) if mode == "dark" else QColor(0, 0, 0)
            
        palette.setColor(QPalette.WindowText, text)
        palette.setColor(QPalette.Text, text)
        palette.setColor(QPalette.ButtonText, text)
        palette.setColor(QPalette.Window, base)
        palette.setColor(QPalette.Base, base)
        app.setPalette(palette)

GlassTheme = ThemeManager()

# --- 4. COMPONENTES UI ---
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

# --- 5. WIDGET NATIVO ---
class NativeGlassWidget(QWidget):
    # AQUI ESTA EL CAMBIO: Agregamos tint_color=None al constructor
    def __init__(self, style=GlassStyle.SIDEBAR, tint_color=None, parent=None, **kwargs):
        super().__init__(parent)
        self._style = style
        self._tint_color = tint_color # Guardamos el tinte personalizado
        self._border_radius = 0
        self._corner_mask = kwargs.get('corner_mask', None)

        GlassTheme.mode_changed.connect(self._on_mode_changed)
        
        # --- CONFIGURACIÓN TRANSPARENCIA (La del Script V3) ---
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setStyleSheet("background: transparent;")
        
        self._layout_proxy = None
        self._shield = None

        if sys.platform == "darwin":
            # macOS: Código original intacto
            self.setAttribute(Qt.WA_NativeWindow, True)
            
            self._root_layout = QVBoxLayout(self)
            self._root_layout.setContentsMargins(0, 0, 0, 0)
            self._root_layout.setSpacing(0)
            
            self._shield = QWidget()
            self._shield.setAttribute(Qt.WA_NativeWindow, True)
            self._shield.setAttribute(Qt.WA_TranslucentBackground, True)
            self._shield.setStyleSheet("background: transparent;")
            
            self._root_layout.addWidget(self._shield)
            self._layout_proxy = QVBoxLayout(self._shield)
            self.content_layout = self._layout_proxy
            
        elif sys.platform == "win32":
            # Windows: Layout directo
            self._layout_proxy = QVBoxLayout(self)
            self.content_layout = self._layout_proxy

        self._layout_proxy.setContentsMargins(0, 0, 0, 0)
        self._layout_proxy.setSpacing(0)

    # --- API ---
    def addWidget(self, widget, stretch=0, alignment=Qt.Alignment()):
        self._layout_proxy.addWidget(widget, stretch, alignment)

    def addLayout(self, layout, stretch=0):
        self._layout_proxy.addLayout(layout, stretch)

    def addStretch(self, stretch=0):
        self._layout_proxy.addStretch(stretch)
        
    def addSpacing(self, size):
        self._layout_proxy.addSpacing(size)
        
    def contentLayout(self):
        return self._layout_proxy

    def setLayout(self, layout):
        if sys.platform == "darwin":
            QWidget().setLayout(self._layout_proxy) 
            self._layout_proxy = layout
            self._shield.setLayout(layout)
            self.content_layout = layout
        else:
            if self.layout():
                QWidget().setLayout(self.layout())
            super().setLayout(layout)
            self._layout_proxy = layout
            self.content_layout = layout

    def showEvent(self, event):
        super().showEvent(event)
        # Aplicamos lógica nativa
        if sys.platform == "win32" and self.isWindow():
             apply_glass_logic(self, self._style, GlassTheme.get_current_mode())
        elif sys.platform == "darwin":
            apply_glass_logic(self, self._style, GlassTheme.get_current_mode())

    def _on_mode_changed(self, mode):
        if sys.platform == "darwin" or (sys.platform == "win32" and self.isWindow()):
            apply_glass_logic(self, self._style, mode)
        self.update()

    def paintEvent(self, event):
        if sys.platform == "win32":
            # --- VENTANA MADRE: NO PINTAR (Bypass total para ver el Acrylic) ---
            if self.isWindow():
                return 

            # --- HIJOS: PINTAR TINTE ---
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            self._paint_windows_material(painter)
        else:
            super().paintEvent(event)

    def _paint_windows_material(self, painter):
        # 1. Limpiar el fondo del widget (para ser transparente)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(self.rect(), Qt.transparent)
        
        # 2. Pintar el Tinte Semitransparente
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        
        mode = GlassTheme.get_current_mode()
        is_dark = (mode == "dark")
        
        # --- DEFINICIÓN DE MATERIALES ---
        
        # AQUI ESTA EL CAMBIO: Prioridad al color personalizado si existe
        if self._tint_color is not None:
            # Si el usuario pasó un tinte, USAMOS ESE
            color = QColor(self._tint_color)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color))
            
        else:
            # Si no, usamos los defaults grises de la librería
            if self._style == GlassStyle.SIDEBAR:
                # Tinte Sidebar: Gris Oscuro/Claro semitransparente
                alpha = 150 if is_dark else 180 
                color = QColor(25, 25, 25, alpha) if is_dark else QColor(245, 245, 245, alpha)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(color))
                
            elif self._style == GlassStyle.HEADER:
                # Header: Muy transparente
                alpha = 40 
                color = QColor(20, 20, 20, alpha) if is_dark else QColor(255, 255, 255, alpha)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(color))
                
            elif self._style in [GlassStyle.POPOVER, GlassStyle.MENU]:
                # Popover: Más marcado
                alpha = 210
                if is_dark:
                    color = QColor(40, 40, 40, alpha)
                    border = QColor(255, 255, 255, 30)
                else:
                    color = QColor(255, 255, 255, alpha)
                    border = QColor(0, 0, 0, 20)
                painter.setPen(QPen(border, 1))
                painter.setBrush(QBrush(color))
                
            else:
                alpha = 100
                color = QColor(128, 128, 128, alpha)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(color))
        
        rect = self.rect()
        r = self._border_radius
        
        if self._style in [GlassStyle.POPOVER, GlassStyle.MENU]:
             rect = rect.adjusted(1, 1, -1, -1)
             if r == 0: r = 8
             
        painter.drawRoundedRect(rect, r, r)


# --- LOGICA NATIVA WINDOWS ---
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
        # SOLO ACTUAMOS EN LA VENTANA MADRE
        if target_object.isWindow():
            
            # 1. Configurar Atributos de Transparencia (V3 Success)
            target_object.setAttribute(Qt.WA_TranslucentBackground, True)
            target_object.setAttribute(Qt.WA_NoSystemBackground, True)
            # Inyección de CSS vital
            target_object.setStyleSheet("background: transparent;")
            
            # 2. Extender Marco al Área Cliente (EL FIX DEL NEGRO)
            margins = MARGINS(-1, -1, -1, -1)
            dwmapi.DwmExtendFrameIntoClientArea(oid, byref(margins))
            
            # 3. Forzar Modo Oscuro (Mejora el Acrylic)
            dark = c_int(1 if use_dark else 0)
            dwmapi.DwmSetWindowAttribute(oid, DWMWA_USE_IMMERSIVE_DARK_MODE, byref(dark), sizeof(dark))
            
            # 4. Activar ACRYLIC (ID 3)
            # Usamos Acrylic porque Mica (2) se ve negro en tu PC.
            backdrop = c_int(DWMSBT_TRANSIENTWINDOW)
            dwmapi.DwmSetWindowAttribute(oid, DWMWA_SYSTEMBACKDROP_TYPE, byref(backdrop), sizeof(backdrop))
            
            # Forzar repintado para quitar residuos
            target_object.repaint()

def apply_glass(target_object, style=GlassStyle.SIDEBAR, mode=None):
    if mode is None:
        mode = GlassTheme.get_current_mode()
    apply_glass_logic(target_object, style, mode)
