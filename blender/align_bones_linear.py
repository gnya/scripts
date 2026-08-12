import bpy
from bpy.types import ArmatureEditBones, EditBone


def align_bones_linear(groups: list[list[EditBone]]):
    for group in groups:
        bgn = [b for b in group if b.parent not in group]
        end = [b for b in group if all(c not in group for c in b.children)]
        bgn = bgn[0] if len(bgn) == 1 else None
        end = end[0] if len(end) == 1 else None

        if bgn is None or end is None:
            raise RuntimeError("begin/end bone was not found.")

        bgn_pos, end_pos = bgn.head, end.tail
        direction = (end_pos - bgn_pos).normalized()

        print(f"{bgn_pos} -> {end_pos}")

        for b in group:
            if b is not bgn:
                b.head = bgn_pos + direction * direction.dot(b.head - bgn_pos)
            if b is not end:
                b.tail = bgn_pos + direction * direction.dot(b.tail - bgn_pos)


def selected_edit_bones(bones: ArmatureEditBones) -> list[list[EditBone]]:
    selected_bones: list[EditBone] = [b for b in bones if b.select]
    groups: list[list[EditBone]] = []

    while len(selected_bones) > 0:
        bone = selected_bones[0]
        group: list[EditBone] = [
            b
            for b in bone.children_recursive
            if b in selected_bones and b.parent in selected_bones
        ]

        while bone and bone in selected_bones:
            group.append(bone)

            bone = bone.parent

        selected_bones = [b for b in selected_bones if b not in group]

        groups.append(group)

    return groups


if __name__ == "__main__":
    obj = bpy.context.object

    if (
        obj
        and obj.data
        and obj.type == "ARMATURE"
        and bpy.context.mode == "EDIT_ARMATURE"
    ):
        # 選択されたボーンを親子関係にあるものごとにグループ分けする
        groups = selected_edit_bones(obj.data.edit_bones)

        # グループにあるボーンごとにボーンの始点と終点を基準に整列させる
        align_bones_linear(groups)
