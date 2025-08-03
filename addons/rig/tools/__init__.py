from .ops_pose import VIEW3D_OT_rig_copy_pose
from .ops_pose import VIEW3D_OT_rig_paste_pose

from .ops_show_bones import VIEW3D_OT_rig_show_animated_bones
from .ops_show_bones import VIEW3D_OT_rig_show_overrided_bones
from .ops_show_bones import VIEW3D_OT_rig_show_prefix_bones

from .ops_asset import VIEW3D_OT_rig_update_asset

from .panels import VIEW3D_PT_rig_tools


classes = (
    VIEW3D_OT_rig_copy_pose,
    VIEW3D_OT_rig_paste_pose,
    VIEW3D_OT_rig_show_animated_bones,
    VIEW3D_OT_rig_show_overrided_bones,
    VIEW3D_OT_rig_show_prefix_bones,
    VIEW3D_OT_rig_update_asset,
    VIEW3D_PT_rig_tools
)


def register():
    from bpy.utils import register_class

    for c in classes:
        register_class(c)


def unregister():
    from bpy.utils import unregister_class

    for c in classes:
        unregister_class(c)
