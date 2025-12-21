# src/native_glass/windows/win32_utils.py
import sys
from ctypes import byref, sizeof, windll, c_bool, c_void_p

# Importamos nuestras estructuras locales
from .c_structures import MONITORINFO

def is_composition_enabled():
    """Detecta si DWM (efectos visuales) está habilitado."""
    bResult = c_bool(False)
    windll.dwmapi.DwmIsCompositionEnabled(byref(bResult))
    return bResult.value

def get_monitor_info(hwnd, dw_flags):
    """Obtiene información del monitor sin usar pywin32."""
    monitor = windll.user32.MonitorFromWindow(int(hwnd), dw_flags)
    if not monitor:
        return None

    info = MONITORINFO()
    info.cbSize = sizeof(MONITORINFO)
    
    windll.user32.GetMonitorInfoW(c_void_p(monitor), byref(info))
    
    return {
        "Monitor": (info.rcMonitor.left, info.rcMonitor.top, info.rcMonitor.right, info.rcMonitor.bottom),
        "Work": (info.rcWork.left, info.rcWork.top, info.rcWork.right, info.rcWork.bottom),
        "Flags": info.dwFlags,
    }

def is_win11():
    """Verifica si es Windows 11 (Build >= 22000)."""
    if sys.platform != "win32":
        return False
    return sys.getwindowsversion().build >= 22000

def get_dpi_for_window(hwnd):
    """Obtiene el DPI de la ventana."""
    try:
        return windll.user32.GetDpiForWindow(int(hwnd))
    except AttributeError:
        hdc = windll.user32.GetDC(int(hwnd))
        if not hdc:
            return 96
        dpi = windll.gdi32.GetDeviceCaps(hdc, 88) # 88 = LOGPIXELSX
        windll.user32.ReleaseDC(int(hwnd), hdc)
        return dpi if dpi > 0 else 96