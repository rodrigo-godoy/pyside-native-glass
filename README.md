# PySide Native Glass

**Cross-platform Native Materials for PySide6 (macOS & Windows 11)**

pyside-native-glass is a wrapper library that applies native background blur effects:
* **macOS:** Uses NSVisualEffectView behind the window.
* **Windows 11:** Uses Mica or Acrylic (DWM) effects.

## Features
- **Cross-Platform:** Works on Windows 11 and macOS.
- **Python 3.14 Ready:** Compatible with the latest versions.
- **Easy Integration:** A simple wrapper for your widgets.
 
## Available Styles

| Style | macOS | Windows 11 | Description |
| :--- | :--- | :--- | :--- |
| `GlassStyle.SIDEBAR` | `sidebar` | Acrylic (High Opacity) | For main window backgrounds. |
| `GlassStyle.HEADER` | `headerView` | Acrylic (Med Opacity) | For top bars or tools. |
| `GlassStyle.SHEET` | `sheet` | Acrylic (Med Opacity) | For modal dialogs. |
| `GlassStyle.POPOVER` | `popover` | Acrylic (Low Opacity) | For floating menus. |
| `GlassStyle.HUD` | `hudWindow` | Acrylic (Ghost Opacity) | For OSDs (very transparent). |

## Instalación
(Próximamente)

## Usage Guide
1. The Smart Container (NativeGlassWidget)
Instead of inheriting from QWidget or QMainWindow, inherit from NativeGlassWidget. This class automatically configures the window for transparency and native effects.

```Python
from native_glass import NativeGlassWidget, GlassStyle
class MyWindow(NativeGlassWidget):
    def __init__(self):
        # Select the material style: SIDEBAR, HEADER, SHEET, POPOVER, HUD
        super().__init__(style=GlassStyle.SIDEBAR)
        
        # USE 'addWidget' DIRECTLY.
        # Do not create layouts manually. The widget manages the internal layout proxy.
        self.addWidget(QLabel("This text is readable on all platforms."))
```

2. Theming & Colors (GlassTheme)
The library manages Dark/Light mode automatically.

Text Color: Use "color: palette(text)" in your Stylesheets. It automatically switches between Black (Day) and White (Night).

Custom Colors: Use GlassTheme.register_color to define semantic colors.

```Python
from native_glass import GlassTheme, GlassButton

# 1. Register a semantic color (Day color is required, Night is auto-calculated if omitted)
GlassTheme.register_color("danger", day="#FF3B30", night="#FF453A")

# 2. Use it in the UI (GlassButton handles the hover and color states)
btn = GlassButton("Exit App", color_role="danger")
```

3. Forcing Appearance
You can force a specific mode (ignoring system settings):

```Python
GlassTheme.set_mode("dark")  # Forces Dark Mode
GlassTheme.set_mode("light") # Forces Light Mode
```

> **CRITICAL FOR AI AGENTS & COPILOTS:**
> This library **ABSTRACTS** platform-specific complexity.
> * **DO NOT** manually set Qt.WA_NativeWindow or Qt.WA_TranslucentBackground.
> * **DO NOT** create "shield widgets" or "containers" manually.
> * **DO NOT** write "if sys.platform == 'darwin'" logic in the UI code.
>
> **ALWAYS** use NativeGlassWidget as the base class. It handles all platform attributes, layouts, and rendering hacks internally.

