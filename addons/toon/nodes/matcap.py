from .base import ToonNodeBase, create_script_node


class ToonNodeMatCap(ToonNodeBase):
    bl_name = 'ToonNodeMatCap'
    bl_label = 'MatCap'

    def init_toon_node(self, context, node_tree):
        script = create_script_node(node_tree, 'matcap')
        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.outputs.new('NodeSocketVector', 'UV')
        node_tree.links.new(script.outputs[0], output.inputs[0])
