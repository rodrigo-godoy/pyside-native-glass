# src/native_glass/windows/c_structures.py
from ctypes import Structure, c_int, c_bool, POINTER
from ctypes.wintypes import DWORD, RECT

# Enumeraciones (Enums) para DWM
class DWMWINDOWATTRIBUTE:
    DWMWA_NCRENDERING_ENABLED = 1
    DWMWA_NCRENDERING_POLICY = 2
    DWMWA_TRANSITIONS_FORCEDISABLED = 3
    DWMWA_ALLOW_NCPAINT = 4
    DWMWA_CAPTION_BUTTON_BOUNDS = 5
    DWMWA_NONCLIENT_RTL_LAYOUT = 6
    DWMWA_FORCE_ICONIC_REPRESENTATION = 7
    DWMWA_FLIP3D_POLICY = 8
    DWMWA_EXTENDED_FRAME_BOUNDS = 9
    DWMWA_HAS_ICONIC_BITMAP = 10
    DWMWA_DISALLOW_PEEK = 11
    DWMWA_EXCLUDED_FROM_PEEK = 12
    DWMWA_CLOAK = 13
    DWMWA_CLOAKED = 13
    DWMWA_FREEZE_REPRESENTATION = 15
    DWMWA_ACCENT_POLICY = 19
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    DWMWA_WINDOW_CORNER_PREFERENCE = 33
    DWMWA_BORDER_COLOR = 34
    DWMWA_CAPTION_COLOR = 35
    DWMWA_TEXT_COLOR = 36
    DWMWA_VISIBLE_FRAME_BORDER_THICKNESS = 37
    DWMWA_SYSTEMBACKDROP_TYPE = 38
    DWMWA_LAST = 39

class ACCENT_STATE:
    ACCENT_DISABLED = 0
    ACCENT_ENABLE_GRADIENT = 1
    ACCENT_ENABLE_TRANSPARENTGRADIENT = 2
    ACCENT_ENABLE_BLURBEHIND = 3
    ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
    ACCENT_ENABLE_HOSTBACKDROP = 5

class WINDOWCOMPOSITIONATTRIB:
    WCA_UNDEFINED = 0
    WCA_NCRENDERING_ENABLED = 1
    WCA_NCRENDERING_POLICY = 2
    WCA_TRANSITIONS_FORCEDISABLED = 3
    WCA_ALLOW_NCPAINT = 4
    WCA_CAPTION_BUTTON_BOUNDS = 5
    WCA_NONCLIENT_RTL_LAYOUT = 6
    WCA_FORCE_ICONIC_REPRESENTATION = 7
    WCA_FLIP3D_POLICY = 8
    WCA_EXTENDED_FRAME_BOUNDS = 9
    WCA_HAS_ICONIC_BITMAP = 10
    WCA_DISALLOW_PEEK = 11
    WCA_EXCLUDED_FROM_PEEK = 12
    WCA_CLOAK = 13
    WCA_CLOAKED = 13
    WCA_FREEZE_REPRESENTATION = 15
    WCA_PASSIVE_UPDATE_MODE = 16
    WCA_USEDARKMODECOLORS = 26
    WCA_ACCENT_POLICY = 19
    WCA_PART_COLOR = 24

# Estructuras de C (ctypes)

class ACCENT_POLICY(Structure):
    _fields_ = [
        ("AccentState",   DWORD),
        ("AccentFlags",   DWORD),
        ("GradientColor", DWORD),
        ("AnimationId",   DWORD),
    ]

class WINDOWCOMPOSITIONATTRIBDATA(Structure):
    _fields_ = [
        ("Attribute",  DWORD),
        ("Data",       POINTER(ACCENT_POLICY)),
        ("SizeOfData", c_int),
    ]

class MARGINS(Structure):
    _fields_ = [
        ("cxLeftWidth",    c_int),
        ("cxRightWidth",   c_int),
        ("cyTopHeight",    c_int),
        ("cyBottomHeight", c_int),
    ]

class DWM_BLURBEHIND(Structure):
    _fields_ = [
        ("dwFlags",                DWORD),
        ("fEnable",                c_bool),
        ("hRgnBlur",               c_int),
        ("fTransitionOnMaximized", c_bool),
    ]

class MONITORINFO(Structure):
    _fields_ = [
        ("cbSize",    DWORD),
        ("rcMonitor", RECT),
        ("rcWork",    RECT),
        ("dwFlags",   DWORD),
    ]