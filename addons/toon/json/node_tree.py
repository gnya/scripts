from bpy.types import Node, NodeTree

from toon.utils import from_node

from .image import encode_image
from .palette import PaletteData, PaletteParseError


def encode_node_tree(node_tree: NodeTree) -> PaletteData:
    palette_data: PaletteData = {'Group': {}}
    entry_to_node: dict[str, dict[str, Node | None]] = {}
    node_to_entry: dict[Node | None, str] = {}

    output_node = node_tree.nodes.get('Group Output')

    for socket_id in range(len(node_tree.outputs)):
        socket = node_tree.outputs[socket_id]
        name = socket.name.split('|', 1)
        group_name = 'Group'
        entry_name = name[-1].strip()

        if len(name) > 1:
            group_name = name[0].strip()

        if group_name not in palette_data:
            palette_data[group_name] = {}

        if group_name not in entry_to_node:
            entry_to_node[group_name] = {}

        entry_data = {}
        node = None

        if output_node is None:
            root = node_tree.outputs[socket_id]

            entry_data = {
                'type': 'COLOR',
                'color': list(root.default_value)
            }
        else:
            root = output_node.inputs[socket_id]
            node = from_node(root)

            if node is None:
                entry_data = {
                    'type': 'COLOR',
                    'color': list(root.default_value)
                }
            elif node.type == 'RGB':
                entry_data = {
                    'type': 'COLOR',
                    'color': node.outputs[0].default_value
                }
            elif node.type == 'TEX_IMAGE':
                uv = from_node(node.inputs[0], find={'UVMAP'})
                entry_data = {
                    'type': 'TEXTURE',
                    'texture_image': encode_image(node.image),
                    'texture_uv_map': '' if uv is None else uv.uv_map
                }
            elif node.type == 'MIX':
                entry_data = {
                    'type': 'MIX',
                    'mix_factor': node.inputs[0].default_value
                }

        if entry_name in palette_data[group_name]:
            raise PaletteParseError(
                f'{socket.name}: The socket name is duplicated.'
            )

        if node is not None and node in node_to_entry:
            raise PaletteParseError(
                f'{node.name}: A node cannot be shared across multiple entries.'
            )

        palette_data[group_name][entry_name] = entry_data
        entry_to_node[group_name][entry_name] = node
        node_to_entry[node] = entry_name

    if len(palette_data['Group']) == 0:
        palette_data.pop('Group')

    # Solve `MIX` type entry.
    for group_name, group_data in palette_data.items():
        for entry_name, entry_data in group_data.items():
            if entry_data['type'] == 'MIX':
                node = entry_to_node[group_name][entry_name]

                if node is None:
                    continue

                node_a = from_node(node.inputs[6])
                node_b = from_node(node.inputs[7])

                entry_data['mix_source_a'] = node_to_entry.get(node_a, '')
                entry_data['mix_source_b'] = node_to_entry.get(node_b, '')

    return palette_data
