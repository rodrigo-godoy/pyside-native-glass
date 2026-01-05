import sys
import os
from enum import Enum
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QPushButton
from PySide6.QtCore import Qt, Signal, QObject
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

    def get_asset(self, filename):
        mode = self.get_current_mode()
        if mode == "light":
            return os.path.join(self._assets_path, filename)
        base, ext = os.path.splitext(filename)
        dark_name = f"{base}_dark{ext}"
        full_dark = os.path.join(self._assets_path, dark_name)
        if os.path.exists(full_dark):
            return full_dark
        return os.path.join(self._assets_path, filename)

    def _calculate_dark_variant(self, hex_color):
        c = QColor(hex_color)
        h, s, lum = c.getHslF()
        new_lum = 1.0 - lum
        new_s = s * 0.8 if new_lum < 0.5 else s
        return QColor.fromHslF(h, new_s, new_lum).name()

    def _apply_qt_palette(self, mode):
        app = QApplication.instance()
        if not app:
            return
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

# --- 3. COMPONENTES UI ---

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

# --- 4. WIDGET PRINCIPAL ---
class NativeGlassWidget(QWidget):
    def __init__(self, style=GlassStyle.SIDEBAR, parent=None):
        super().__init__(parent)
        self._style = style
        # Radio por defecto para la simulación en Windows hijos
        self._border_radius = 16 
        GlassTheme.mode_changed.connect(self._on_mode_changed)
        
        # Configuración base: Transparente para que Qt no pinte fondo sólido
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")
        
        self._layout_proxy = None
        self._shield = None

        # --- LÓGICA DE PLATAFORMA ---
        if sys.platform == "darwin":
            # macOS: Siempre nativo, siempre anidado. Funciona perfecto.
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
            # Windows: Lógica Híbrida para evitar Ghosting.
            
            # Si es ventana principal (sin padre) -> Activar DWM nativo
            if self.isWindow():
                self.setAttribute(Qt.WA_NativeWindow, True)
                self.setAttribute(Qt.WA_NoSystemBackground, True)
                self._layout_proxy = QVBoxLayout(self)
            else:
                # Si es hijo -> NO NativeWindow. Usar simulación de pintado.
                self.setAttribute(Qt.WA_NativeWindow, False)
                self._layout_proxy = QVBoxLayout(self)

        self._layout_proxy.setContentsMargins(0, 0, 0, 0)
        self._layout_proxy.setSpacing(0)

    # --- API PÚBLICA ---
    def addWidget(self, widget, stretch=0, alignment=Qt.Alignment()):
        self._layout_proxy.addWidget(widget, stretch, alignment)

    def addLayout(self, layout, stretch=0):
        self._layout_proxy.addLayout(layout, stretch)

    def addStretch(self, stretch=0):
        self._layout_proxy.addStretch(stretch)
        
    def addSpacing(self, size):
        self._layout_proxy.addSpacing(size)
        
    def setRadius(self, radius):
        """Ajusta el radio de borde en modo simulado (Windows Child)."""
        self._border_radius = radius
        self.update()

    def contentLayout(self):
        return self._layout_proxy

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
        # Aplicar efecto nativo SOLO si es macOS o Windows Top-Level
        if sys.platform == "darwin" or (sys.platform == "win32" and self.isWindow()):
            self._apply_effect()
            if sys.platform == "win32":
                self.window().repaint()

    def _on_mode_changed(self, mode):
        if sys.platform == "darwin" or (sys.platform == "win32" and self.isWindow()):
            self._apply_effect()
        self.update()

    def paintEvent(self, event):
        if sys.platform == "win32":
            if self.isWindow():
                # TopLevel: Limpiar para dejar ver el Acrylic del DWM
                painter = QPainter(self)
                painter.setCompositionMode(QPainter.CompositionMode_Clear)
                painter.fillRect(self.rect(), Qt.transparent)
            else:
                # Hijo: Simular material con tintado
                self._paint_windows_simulation()
        else:
            super().paintEvent(event)

    def _paint_windows_simulation(self):
        """Simula el material pintando un tinte semitransparente."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        mode = GlassTheme.get_current_mode()
        is_dark = (mode == "dark")
        
        # Colores ajustados para ser notorios pero elegantes
        if self._style == GlassStyle.SIDEBAR:
            # Oscuro/Claro denso
            color = QColor(25, 25, 25, 180) if is_dark else QColor(240, 240, 240, 180)
        elif self._style == GlassStyle.POPOVER:
            # Muy transparente
            color = QColor(40, 40, 40, 120) if is_dark else QColor(255, 255, 255, 120)
        elif self._style == GlassStyle.HEADER:
            color = QColor(30, 30, 30, 150) if is_dark else QColor(245, 245, 245, 150)
        elif self._style == GlassStyle.HUD:
            color = QColor(10, 10, 10, 60) if is_dark else QColor(255, 255, 255, 60)
        else:
            color = QColor(30, 30, 30, 200) if is_dark else QColor(255, 255, 255, 200)

        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
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
        
        # Color base para el tinte nativo del DWM (Ventana Principal)
        bg = "050505" if use_dark else "F2F2F2"
        
        # Ajuste de opacidad de la ventana madre
        if style in [GlassStyle.SIDEBAR, GlassStyle.FULL]:
            alpha = "B0" if use_dark else "A0"
        elif style in [GlassStyle.HEADER, GlassStyle.SHEET]:
            alpha = "90" if use_dark else "80"
        elif style in [GlassStyle.MENU, GlassStyle.POPOVER]:
            alpha = "70" if use_dark else "60"
        elif style == GlassStyle.HUD:
            alpha = "20"
        else:
            alpha = "99"
            
        color_hex = f"{alpha}{bg}"
        effect.setAcrylicEffect(oid, gradientColor=color_hex, isDarkMode=use_dark)

def apply_glass(target_object, style=GlassStyle.SIDEBAR, mode=None):
    if mode is None:
        mode = GlassTheme.get_current_mode()
    apply_glass_logic(target_object, style, mode)