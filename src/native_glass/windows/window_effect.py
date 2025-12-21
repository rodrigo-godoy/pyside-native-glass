# src/native_glass/windows/window_effect.py
from ctypes import byref, c_int, pointer, sizeof, windll

from .c_structures import (
    ACCENT_POLICY,
    ACCENT_STATE,
    DWMWINDOWATTRIBUTE,
    MARGINS,
    WINDOWCOMPOSITIONATTRIB,
    WINDOWCOMPOSITIONATTRIBDATA,
)
from .win32_utils import is_win11


class WindowsWindowEffect:
    def __init__(self, target):
        self.target = target

    def setMicaEffect(self, hwnd, isDarkMode=True, isAlt=False):
        """
        Aplica Mica (Opaco, tintado con wallpaper).
        Solo funciona en Windows 11.
        """
        hwnd = int(hwnd)

        if not is_win11():
            # Fallback a Acrylic si no es Win11
            color = "20202099" if isDarkMode else "F2F2F299"
            self.setAcrylicEffect(hwnd, color, isDarkMode)
            return

        # 1. Configurar Modo Oscuro en la Barra de Título
        darkMode = c_int(1 if isDarkMode else 0)
        windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWINDOWATTRIBUTE.DWMWA_USE_IMMERSIVE_DARK_MODE,
            byref(darkMode),
            sizeof(darkMode),
        )

        # 2. Configurar Mica
        # DWMWA_SYSTEMBACKDROP_TYPE: 2 = Mica, 4 = Mica Alt
        backdropValue = c_int(4 if isAlt else 2)

        windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWINDOWATTRIBUTE.DWMWA_SYSTEMBACKDROP_TYPE,
            byref(backdropValue),
            sizeof(backdropValue),
        )

        # Extender frame al cliente para que se pinte el fondo
        self._extend_frame(hwnd)

    def setAcrylicEffect(self, hwnd, gradientColor="00000000", isDarkMode=True):
        """
        Aplica Acrylic (Blur translúcido).
        Funciona en Win 10 y 11.
        gradientColor: Hex String AABBGGRR.
        """
        hwnd = int(hwnd)

        # Color hexadecimal a entero
        # Se espera AABBGGRR en hex string
        try:
            color_int = int(gradientColor, 16)
        except Exception:  # CORREGIDO: Usamos Exception en lugar de bare except
            color_int = 0x99000000  # Fallback negro

        accent = ACCENT_POLICY()
        accent.AccentState = ACCENT_STATE.ACCENT_ENABLE_ACRYLICBLURBEHIND
        accent.GradientColor = color_int
        # Flags opcionales
        accent.AccentFlags = (
            2  # DrawLeftBorder | DrawTopBorder... a veces ayuda a bordes suaves
        )

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_ACCENT_POLICY
        data.SizeOfData = sizeof(accent)
        data.Data = pointer(accent)

        # Llamada a API no documentada de User32
        windll.user32.SetWindowCompositionAttribute(hwnd, byref(data))

        # También seteamos el modo oscuro para los controles de ventana
        darkMode = c_int(1 if isDarkMode else 0)
        windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWINDOWATTRIBUTE.DWMWA_USE_IMMERSIVE_DARK_MODE,
            byref(darkMode),
            sizeof(darkMode),
        )

    def _extend_frame(self, hwnd):
        # Mágia negra para quitar el fondo sólido de Win32 y dejar ver el DWM
        margins = MARGINS(-1, -1, -1, -1)
        windll.dwmapi.DwmExtendFrameIntoClientArea(hwnd, byref(margins))