import bpy

from rig import ui_drawer

from .bones import check_ik_fk_bones


def _UI_CONTENTS(group, lr, parent):
    return {
        '$view3d.rig_snap_ik_to_fk': {
            '': ('', 'IK → FK', '', 0, 1.0)
        },
        '$view3d.rig_snap_fk_to_ik': {
            '': ('', 'FK → IK', '', 1, 1.0)
        },
        'pose.bones["CTR_properties_body"]': {
            f'["fk_{group}.{lr}"]': ('', 'IK - FK', '', 2, 1.0),
            f'["ik_stretch_{group}s"]': ('', 'IK Stretch', '', 3, 1.0),
            f'["ik_{group}_pole_parent.{lr}"]': ('', 'IK Pole Parent', '', 4, 1.0),
            f'["ik_{group}_parent.{lr}"]': ('', '', '', 6, 0.3)
        },
        '$view3d.rig_set_ik_parent': {
            'type': ('', f'IK Parent ({parent})', '', 5, 0.7)
        }
    }


class VIEW3D_PT_rig_ikfk(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rig_ikfk'
    bl_label = 'IK/FK'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'VIEW3D_PT_rig_main'

    @classmethod
    def poll(cls, context):
        bones = context.selected_pose_bones

        if not bones:
            return False

        groups = check_ik_fk_bones(bones)

        return True if groups else False

    def draw(self, context):
        layout = self.layout

        bones = context.selected_pose_bones
        groups = check_ik_fk_bones(bones)
        groups = sorted(list(groups), key=lambda g: g[0].name + g[1] + g[3])

        for obj, group, _, lr in groups:
            parent = ''
            props_body = obj.pose.bones["CTR_properties_body"]

            match props_body[f'ik_{group}_parent.{lr}']:
                case 0:
                    parent = 'Root'
                case 1:
                    parent = 'Torso'
                case 2:
                    parent = 'Chest'

            box = layout.box()

            row = box.row()
            row.alignment = 'CENTER'
            row.label(text=f'{group}.{lr} ({obj.name})', translate=False)

            contents = {}
            props = _UI_CONTENTS(group, lr, parent)
            ui_drawer.collect_contents(contents, obj, props)

            operator_args = {
                'bone_group': group,
                'bone_lr': lr
            }
            box.context_pointer_set('snap_target', obj)
            box.context_pointer_set('props_body', props_body)
            ui_drawer.draw_contents(box, contents, operator_args)
