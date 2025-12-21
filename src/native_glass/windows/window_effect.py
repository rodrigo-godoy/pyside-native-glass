# src/native_glass/windows/window_effect.py
import warnings
from ctypes import WinDLL, c_bool, c_int, pointer, sizeof, byref
from ctypes.wintypes import DWORD, LPCVOID

from PySide6.QtGui import QColor

from .c_structures import (
    ACCENT_POLICY, ACCENT_STATE, WINDOWCOMPOSITIONATTRIB,
    WINDOWCOMPOSITIONATTRIBDATA, DWMWINDOWATTRIBUTE, MARGINS
)
from .win32_utils import is_win11

class WindowsWindowEffect:
    """Implementación de efectos nativos para Windows usando ctypes puro."""

    def __init__(self, window):
        self.window = window
        
        # Cargamos las librerías del sistema (DLLs)
        self.user32 = WinDLL("user32")
        self.dwmapi = WinDLL("dwmapi")
        
        # Mapeamos las funciones de la API de Windows
        self.SetWindowCompositionAttribute = self.user32.SetWindowCompositionAttribute
        self.DwmExtendFrameIntoClientArea = self.dwmapi.DwmExtendFrameIntoClientArea
        self.DwmSetWindowAttribute = self.dwmapi.DwmSetWindowAttribute

        # Definimos los tipos de retorno y argumentos para evitar crasheos en 64-bits
        self.SetWindowCompositionAttribute.restype = c_bool
        self.SetWindowCompositionAttribute.argtypes = [c_int, pointer(WINDOWCOMPOSITIONATTRIBDATA)]
        
        self.DwmSetWindowAttribute.restype = c_int
        self.DwmSetWindowAttribute.argtypes = [c_int, DWORD, LPCVOID, DWORD]
        
        self.DwmExtendFrameIntoClientArea.restype = c_int
        self.DwmExtendFrameIntoClientArea.argtypes = [c_int, pointer(MARGINS)]

        # Inicializamos estructuras reutilizables
        self.accentPolicy = ACCENT_POLICY()
        self.winCompAttrData = WINDOWCOMPOSITIONATTRIBDATA()
        self.winCompAttrData.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_ACCENT_POLICY
        self.winCompAttrData.SizeOfData = sizeof(self.accentPolicy)
        self.winCompAttrData.Data = pointer(self.accentPolicy)

    def setAcrylicEffect(self, hWnd, gradientColor="F2F2F299", enableShadow=True, animationId=0):
        """Aplica efecto Acrylic (Windows 10+)."""
        hWnd = int(hWnd)
        
        try:
            # Procesamiento básico de color (ajustar según necesidad real)
            # El string viene como RRGGBBAA, Windows espera AABBGGRR (casi)
            gradientColor = ''.join(gradientColor[i:i+2] for i in range(6, -1, -2))
            dwGradientColor = DWORD(int(gradientColor, base=16))
        except ValueError:
            dwGradientColor = DWORD(0)

        accentFlags = DWORD(0x20 | 0x40 | 0x80 | 0x100) if enableShadow else DWORD(0)
        
        self.accentPolicy.AccentState = ACCENT_STATE.ACCENT_ENABLE_ACRYLICBLURBEHIND
        self.accentPolicy.GradientColor = dwGradientColor
        self.accentPolicy.AccentFlags = accentFlags
        self.accentPolicy.AnimationId = DWORD(animationId)
        
        self.winCompAttrData.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_ACCENT_POLICY
        self.SetWindowCompositionAttribute(hWnd, pointer(self.winCompAttrData))

    def setMicaEffect(self, hWnd, isDarkMode=False, isAlt=False):
        """Aplica efecto Mica (Solo Windows 11)."""
        if not is_win11():
            warnings.warn("El efecto Mica solo está disponible en Windows 11")
            return

        hWnd = int(hWnd)
        
        # Extendemos el marco al área del cliente (truco necesario para Mica)
        margins = MARGINS(-1, -1, -1, -1) # -1 extiende a todo
        self.DwmExtendFrameIntoClientArea(hWnd, byref(margins))

        # Configurar la política de acento a HostBackdrop
        self.accentPolicy.AccentState = ACCENT_STATE.ACCENT_ENABLE_HOSTBACKDROP
        self.winCompAttrData.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_ACCENT_POLICY
        self.SetWindowCompositionAttribute(hWnd, pointer(self.winCompAttrData))

        # Configurar modo oscuro inmersivo
        value = c_int(1 if isDarkMode else 0)
        self.DwmSetWindowAttribute(
            hWnd, 
            DWMWINDOWATTRIBUTE.DWMWA_USE_IMMERSIVE_DARK_MODE, 
            byref(value), 
            4
        )

        # Configurar tipo de Mica (Normal o Alt)
        # 2 = DWM_SYSTEMBACKDROP_TYPE.MICA
        # 4 = DWM_SYSTEMBACKDROP_TYPE.TABBED (Mica Alt)
        backdrop_value = c_int(4 if isAlt else 2)
        self.DwmSetWindowAttribute(
            hWnd,
            DWMWINDOWATTRIBUTE.DWMWA_SYSTEMBACKDROP_TYPE,
            byref(backdrop_value),
            4
        )

    def removeBackgroundEffect(self, hWnd):
        """Elimina cualquier efecto de fondo y restaura la ventana normal."""
        hWnd = int(hWnd)
        self.accentPolicy.AccentState = ACCENT_STATE.ACCENT_DISABLED
        self.SetWindowCompositionAttribute(hWnd, pointer(self.winCompAttrData))

    def setBorderAccentColor(self, hWnd, color: QColor):
        """Establece el color del borde nativo (Windows 11)."""
        if not is_win11():
            return
        
        hWnd = int(hWnd)
        # Windows usa formato 0x00BBGGRR
        color_ref = DWORD(color.red() | (color.green() << 8) | (color.blue() << 16))
        
        self.DwmSetWindowAttribute(
            hWnd,
            DWMWINDOWATTRIBUTE.DWMWA_BORDER_COLOR,
            byref(color_ref),
            4
        )