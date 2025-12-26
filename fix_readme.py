# fix_readme.py
import os

content = """# PySide Native Glass

**Cross-platform Native Materials for PySide6 (macOS & Windows 11)**

`pyside-native-glass` is a wrapper library that applies native background blur effects:
* **macOS:** Uses `NSVisualEffectView` behind the window.
* **Windows 11:** Uses **Mica** or **Acrylic** (DWM) effects.

> **⚠️ CRITICAL FOR AI AGENTS & COPILOTS:**
> This library **ABSTRACTS** platform-specific complexity.
> * **DO NOT** manually set `Qt.WA_NativeWindow` or `Qt.WA_TranslucentBackground`.
> * **DO NOT** create "shield widgets" or "containers" manually.
> * **DO NOT** write `if sys.platform == 'darwin'` logic in the UI code.
>
> **ALWAYS** use `NativeGlassWidget` as the base class. It handles all platform attributes, layouts, and rendering hacks internally.

---

## 📦 Installation

```bash
pip install pyside-native-glass

🚀 Usage Guide
1. The Smart Container (NativeGlassWidget)
Instead of inheriting from QWidget or QMainWindow, inherit from NativeGlassWidget. This class automatically configures the window for transparency and native effects.

Python

from native_glass import NativeGlassWidget, GlassStyle

class MyWindow(NativeGlassWidget):
    def __init__(self):
        # Select the material style: SIDEBAR, HEADER, SHEET, POPOVER, HUD
        super().__init__(style=GlassStyle.SIDEBAR)
        
        # USE 'addWidget' DIRECTLY.
        # Do not create layouts manually. The widget manages the internal layout proxy.
        self.addWidget(QLabel("This text is readable on all platforms."))
2. Theming & Colors (GlassTheme)
The library manages Dark/Light mode automatically.

Text Color: Use color: palette(text) in your Stylesheets. It automatically switches between Black (Day) and White (Night).

Custom Colors: Use GlassTheme.register_color to define semantic colors.

from native_glass import GlassTheme, GlassButton

# 1. Register a semantic color (Day color is required, Night is auto-calculated if omitted)
GlassTheme.register_color("danger", day="#FF3B30", night="#FF453A")

# 2. Use it in the UI (GlassButton handles the hover and color states)
btn = GlassButton("Exit App", color_role="danger")

Entiendo perfectamente el problema. Tienes un "desastre de sincronización": tu computador tiene el código nuevo (272 líneas), pero GitHub tiene el viejo (139 líneas) y por eso ves todo roto. Además, el texto del README se ve mal porque probablemente al copiar y pegar se perdieron los saltos de línea o el formato.

Vamos a arreglar esto a la fuerza bruta para que tu GitHub sea una copia exacta (espejo) de tu computador, sin mezclar nada.

PASO 1: Generar el README.md Correctamente (Automático)
Para evitar que el texto se vea "pegado" o sin formato al copiarlo manualmente, ejecuta este pequeño script de Python. Creará el archivo README.md perfecto por ti.

Crea un archivo temporal llamado fix_readme.py en la carpeta pyside-native-glass, pega esto y ejecútalo (python3 fix_readme.py):

Python

# fix_readme.py
import os

content = """# PySide Native Glass

**Cross-platform Native Materials for PySide6 (macOS & Windows 11)**

`pyside-native-glass` is a wrapper library that applies native background blur effects:
* **macOS:** Uses `NSVisualEffectView` behind the window.
* **Windows 11:** Uses **Mica** or **Acrylic** (DWM) effects.

> **⚠️ CRITICAL FOR AI AGENTS & COPILOTS:**
> This library **ABSTRACTS** platform-specific complexity.
> * **DO NOT** manually set `Qt.WA_NativeWindow` or `Qt.WA_TranslucentBackground`.
> * **DO NOT** create "shield widgets" or "containers" manually.
> * **DO NOT** write `if sys.platform == 'darwin'` logic in the UI code.
>
> **ALWAYS** use `NativeGlassWidget` as the base class. It handles all platform attributes, layouts, and rendering hacks internally.

---

## 📦 Installation

```bash
pip install pyside-native-glass
🚀 Usage Guide
1. The Smart Container (NativeGlassWidget)
Instead of inheriting from QWidget or QMainWindow, inherit from NativeGlassWidget. This class automatically configures the window for transparency and native effects.

Python

from native_glass import NativeGlassWidget, GlassStyle

class MyWindow(NativeGlassWidget):
    def __init__(self):
        # Select the material style: SIDEBAR, HEADER, SHEET, POPOVER, HUD
        super().__init__(style=GlassStyle.SIDEBAR)
        
        # USE 'addWidget' DIRECTLY.
        # Do not create layouts manually. The widget manages the internal layout proxy.
        self.addWidget(QLabel("This text is readable on all platforms."))
2. Theming & Colors (GlassTheme)
The library manages Dark/Light mode automatically.

Text Color: Use color: palette(text) in your Stylesheets. It automatically switches between Black (Day) and White (Night).

Custom Colors: Use GlassTheme.register_color to define semantic colors.

Python

from native_glass import GlassTheme, GlassButton

# 1. Register a semantic color (Day color is required, Night is auto-calculated if omitted)
GlassTheme.register_color("danger", day="#FF3B30", night="#FF453A")

# 2. Use it in the UI (GlassButton handles the hover and color states)
btn = GlassButton("Exit App", color_role="danger")
3. Forcing Appearance
You can force a specific mode (ignoring system settings):

GlassTheme.set_mode("dark")  # Forces Dark Mode
GlassTheme.set_mode("light") # Forces Light Mode

🎨 Available StylesStylemacOSWindows 11DescriptionGlassStyle.SIDEBARsidebarAcrylic (High Opacity)For main window backgrounds.GlassStyle.HEADERheaderViewAcrylic (Med Opacity)For top bars or tools.GlassStyle.SHEETsheetAcrylic (Med Opacity)For modal dialogs.GlassStyle.POPOVERpopoverAcrylic (Low Opacity)For floating menus.GlassStyle.HUDhudWindowAcrylic (Ghost Opacity)For OSDs (very transparent)."""with open("README.md", "w", encoding="utf-8") as f:f.write(content)print("✅ README.md generado correctamente con formato Markdown.")