from bpy.types import NodeTree


class ToonPaletteColor(object):
    def __init__(self, index: int, node_tree: NodeTree) -> None:
        self.socket_index = index
        self.node_tree = node_tree

    @property
    def name(self) -> str:
        return self.node_tree.outputs[self.socket_index].name

    @name.setter
    def name(self, value: str):
        self.node_tree.outputs[self.socket_index].name = value
