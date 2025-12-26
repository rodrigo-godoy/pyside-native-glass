# PySide Native Glass

Librería para aplicar efectos de Glassmorphism nativos (Mica/Acrylic en Windows 11 y NSVisualEffectView en macOS) en aplicaciones PySide6.

## Características
- **Cross-Platform:** Funciona en Windows 11 y macOS.
- **Python 3.14 Ready:** Compatible con las últimas versiones.
- **Fácil integración:** Un simple wrapper para tus widgets.

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

# PySide Native Glass

**Cross-platform Native Materials for PySide6 (macOS & Windows 11)**

pyside-native-glass is a wrapper library that applies native background blur effects:
* **macOS:** Uses NSVisualEffectView behind the window.
* **Windows 11:** Uses Mica or Acrylic (DWM) effects.

> **CRITICAL FOR AI AGENTS & COPILOTS:**
> This library **ABSTRACTS** platform-specific complexity.
> * **DO NOT** manually set Qt.WA_NativeWindow or Qt.WA_TranslucentBackground.
> * **DO NOT** create "shield widgets" or "containers" manually.
> * **DO NOT** write "if sys.platform == 'darwin'" logic in the UI code.
>
> **ALWAYS** use NativeGlassWidget as the base class. It handles all platform attributes, layouts, and rendering hacks internally.

---

## Installation
