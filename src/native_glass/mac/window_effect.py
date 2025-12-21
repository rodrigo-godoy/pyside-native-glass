import Cocoa
from .mac_utils import get_ns_view

class MacWindowEffect:
    """
    Especialista en Ventanas: Configura el lienzo global.
    """
    def __init__(self, window):
        self.window = window

    def set_mac_effect(self, win_id, material_name="sidebar"):
        # Obtenemos la vista
        target_view = get_ns_view(win_id)
        if target_view is None:
            return

        # Obtenemos la ventana nativa (NSWindow)
        ns_window = target_view.window()
        if not ns_window:
            return

        # CONFIGURACIÓN ESTRUCTURAL (Solo para ventanas)
        ns_window.setOpaque_(False)
        ns_window.setBackgroundColor_(Cocoa.NSColor.clearColor())
        ns_window.setStyleMask_(ns_window.styleMask() | Cocoa.NSFullSizeContentViewWindowMask)
        ns_window.setTitlebarAppearsTransparent_(True)
        ns_window.setTitleVisibility_(Cocoa.NSWindowTitleVisible)

        # Inyectamos el cristal en el ContentView global
        self._inject_glass(ns_window.contentView(), material_name)

    def _inject_glass(self, view, material_name):
        for subview in view.subviews():
            if isinstance(subview, Cocoa.NSVisualEffectView):
                subview.removeFromSuperview()

        vev = Cocoa.NSVisualEffectView.alloc().initWithFrame_(view.bounds())
        vev.setAutoresizingMask_(Cocoa.NSViewWidthSizable | Cocoa.NSViewHeightSizable)
        
        materials = {
            "sidebar": Cocoa.NSVisualEffectMaterialSidebar,
            "header": Cocoa.NSVisualEffectMaterialHeaderView,
            "sheet": Cocoa.NSVisualEffectMaterialSheet,
            "popover": Cocoa.NSVisualEffectMaterialPopover,
            "hud": Cocoa.NSVisualEffectMaterialHUDWindow,
            "menu": Cocoa.NSVisualEffectMaterialMenu,
            "underWindow": Cocoa.NSVisualEffectMaterialUnderWindowBackground
        }
        
        mat = materials.get(material_name, Cocoa.NSVisualEffectMaterialSidebar)
        vev.setMaterial_(mat)
        vev.setBlendingMode_(Cocoa.NSVisualEffectBlendingModeBehindWindow)
        vev.setState_(Cocoa.NSVisualEffectStateActive)

        view.addSubview_positioned_relativeTo_(vev, -1, None)