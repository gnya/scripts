from toon.utils import override

import bpy

from bpy.types import NodeTree

from .base import ToonNodeGroup


class ToonNodeMatCap(ToonNodeGroup):
    bl_idname = 'ToonNodeMatCap'
    bl_label = 'MatCap'

    @override
    def new_node_tree(self, name: str) -> NodeTree:
        node_tree = bpy.data.node_groups.new(name, 'ShaderNodeTree')

        node_tree.outputs.new('NodeSocketVector', 'UV')

        geo = node_tree.nodes.new('ShaderNodeNewGeometry')

        # vector N_cam = normalize(transform("world", "camera", N));
        trans_n = node_tree.nodes.new('ShaderNodeVectorTransform')
        trans_n.convert_to = 'CAMERA'
        trans_n.vector_type = 'NORMAL'
        node_tree.links.new(geo.outputs[1], trans_n.inputs[0])

        # vector I_cam = normalize(transform("world", "camera", I));
        trans_i = node_tree.nodes.new('ShaderNodeVectorTransform')
        trans_i.convert_to = 'CAMERA'
        trans_i.vector_type = 'NORMAL'
        node_tree.links.new(geo.outputs[4], trans_i.inputs[0])

        # vector NI = cross(N_cam, I_cam);
        cross = node_tree.nodes.new('ShaderNodeVectorMath')
        cross.operation = 'CROSS_PRODUCT'
        node_tree.links.new(trans_n.outputs[0], cross.inputs[0])
        node_tree.links.new(trans_i.outputs[0], cross.inputs[1])

        # UV = normalize(vector(NI[1], -NI[0], 0.0)) * length(NI);
        to_xyz = node_tree.nodes.new('ShaderNodeSeparateXYZ')
        node_tree.links.new(cross.outputs[0], to_xyz.inputs[0])

        mul = node_tree.nodes.new('ShaderNodeMath')
        mul.operation = 'MULTIPLY'
        mul.inputs[1].default_value = -1.0
        node_tree.links.new(to_xyz.outputs[0], mul.inputs[0])

        from_xyz = node_tree.nodes.new('ShaderNodeCombineXYZ')
        node_tree.links.new(to_xyz.outputs[1], from_xyz.inputs[0])
        node_tree.links.new(mul.outputs[0], from_xyz.inputs[1])

        norm = node_tree.nodes.new('ShaderNodeVectorMath')
        norm.operation = 'NORMALIZE'
        node_tree.links.new(from_xyz.outputs[0], norm.inputs[0])

        length = node_tree.nodes.new('ShaderNodeVectorMath')
        length.operation = 'LENGTH'
        node_tree.links.new(cross.outputs[0], length.inputs[0])

        scale = node_tree.nodes.new('ShaderNodeVectorMath')
        scale.operation = 'SCALE'
        node_tree.links.new(norm.outputs[0], scale.inputs[0])
        node_tree.links.new(length.outputs[1], scale.inputs[3])

        # UV = UV * 0.5 + vector(0.5, 0.5, 0.0);
        mul_add = node_tree.nodes.new('ShaderNodeVectorMath')
        mul_add.operation = 'MULTIPLY_ADD'
        mul_add.inputs[1].default_value = (0.5, 0.5, 0.5)
        mul_add.inputs[2].default_value = (0.5, 0.5, 0.0)
        node_tree.links.new(scale.outputs[0], mul_add.inputs[0])

        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.links.new(mul_add.outputs[0], output.inputs[0])

        return node_tree
