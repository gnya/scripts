from .ops import VIEW3D_OT_rig_set_ik_parent
from .ops import VIEW3D_OT_rig_snap_fk_to_ik
from .ops import VIEW3D_OT_rig_snap_ik_to_fk

from .panels import VIEW3D_PT_rig_ikfk


classes = (
    VIEW3D_OT_rig_set_ik_parent,
    VIEW3D_OT_rig_snap_fk_to_ik,
    VIEW3D_OT_rig_snap_ik_to_fk,
    VIEW3D_PT_rig_ikfk
)


def register():
    from bpy.utils import register_class

    for c in classes:
        register_class(c)


def unregister():
    from bpy.utils import unregister_class

    for c in classes:
        unregister_class(c)
