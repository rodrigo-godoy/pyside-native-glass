import Cocoa
from .mac_utils import get_ns_view

class MacWidgetEffect:
    """
    Especialista en Widgets: Aplica cristal a componentes internos.
    Ahora soporta forzado de modo (Dark/Light).
    """
    def set_effect(self, widget_id, material_name="sidebar", mode="system"):
        # 1. Obtener la vista
        target_view = get_ns_view(widget_id)
        if target_view is None:
            return

        # 2. Limpieza
        for subview in target_view.subviews():
            if isinstance(subview, Cocoa.NSVisualEffectView):
                subview.removeFromSuperview()

        # 3. Crear cristal
        vev = Cocoa.NSVisualEffectView.alloc().initWithFrame_(target_view.bounds())
        vev.setAutoresizingMask_(Cocoa.NSViewWidthSizable | Cocoa.NSViewHeightSizable)
        
        # --- NUEVO: FORZAR MODO EN EL WIDGET ---
        if mode == "dark":
            vev.setAppearance_(Cocoa.NSAppearance.appearanceNamed_("NSAppearanceNameDarkAqua"))
        elif mode == "light":
            vev.setAppearance_(Cocoa.NSAppearance.appearanceNamed_("NSAppearanceNameAqua"))
        else:
            vev.setAppearance_(None) # Hereda del sistema
        # ---------------------------------------

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

        target_view.addSubview_positioned_relativeTo_(vev, -1, None)