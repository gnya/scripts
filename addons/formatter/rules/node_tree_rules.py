from mathutils import Vector
from . import utils
from .rules import Report, NodeTreeRule


# Align node-tree's right top corner
class NodeTreeAlignRule(NodeTreeRule):
    @classmethod
    def fix_node_tree(cls, node_tree, **kwargs):
        default_corner = kwargs.get('corner', Vector((300.0, 300.0)))
        corner = Vector((-float('inf'), -float('inf')))

        for n in node_tree.nodes:
            loc = utils.node_location_absolute(n)

            if n.type != 'FRAME':
                if loc.x > corner.x:
                    corner.x = loc.x

                if loc.y > corner.y:
                    corner.y = loc.y

        if corner != default_corner:
            name = kwargs['name']
            offset = default_corner - corner

            for n in node_tree.nodes:
                if not n.parent:
                    n.location = n.location + offset

            return Report.log(f'Align "{name}" node_tree')

        return Report.nothing()
