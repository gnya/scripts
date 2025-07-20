from .ops import VIEW3D_OT_rig_attach_light
from .ops import VIEW3D_OT_rig_copy_pose
from .ops import VIEW3D_OT_rig_copy_whole_pose
from .ops import VIEW3D_OT_rig_paste_pose
from .ops import VIEW3D_OT_rig_show_animated_bones

from .panels import VIEW3D_PT_rig_props


classes = (
    VIEW3D_OT_rig_attach_light,
    VIEW3D_OT_rig_copy_pose,
    VIEW3D_OT_rig_paste_pose,
    VIEW3D_OT_rig_copy_whole_pose,
    VIEW3D_OT_rig_show_animated_bones,
    VIEW3D_PT_rig_props
)


def register():
    from bpy.utils import register_class

    for c in classes:
        register_class(c)


def unregister():
    from bpy.utils import unregister_class

    for c in classes:
        unregister_class(c)
