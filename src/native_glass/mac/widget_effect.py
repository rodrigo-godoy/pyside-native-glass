import Cocoa
from .mac_utils import get_ns_view

class MacWidgetEffect:
    """
    Especialista en Widgets: Solo aplica cristal a componentes internos.
    NO toca la configuración de la ventana padre.
    """
    def set_effect(self, widget_id, material_name="sidebar"):
        # 1. Obtener la vista del widget específico
        target_view = get_ns_view(widget_id)
        if target_view is None:
            return

        # 2. Limpieza quirúrgica: Solo quitamos efectos viejos en ESTE widget
        for subview in target_view.subviews():
            if isinstance(subview, Cocoa.NSVisualEffectView):
                subview.removeFromSuperview()

        # 3. Crear el cristal local
        vev = Cocoa.NSVisualEffectView.alloc().initWithFrame_(target_view.bounds())
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

        # 4. Pegar al fondo del widget (-1)
        target_view.addSubview_positioned_relativeTo_(vev, -1, None)