import objc
from ctypes import c_void_p

def get_ns_view(win_id):
    """
    Obtiene el puntero al NSView nativo de un widget específico.
    Es vital para el nuevo widget_effect.py.
    """
    ptr = c_void_p(int(win_id))
    return objc.objc_object(c_void_p=ptr)