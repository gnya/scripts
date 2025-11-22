from typing import Any

from bpy.types import Node, NodeSocket


class NodeLinkRebinder():
    def __init__(self, node: Node):
        self.node = node
        self.inputs: dict[str, list[NodeSocket]] = {}
        self.outputs: dict[str, list[NodeSocket]] = {}

    def __enter__(self):
        for input in self.node.inputs:
            if input.enabled:
                sockets = [l.from_socket for l in input.links]
                self.inputs[input.name] = sockets

        for output in self.node.outputs:
            if output.enabled:
                sockets = [l.to_socket for l in output.links]
                self.outputs[output.name] = sockets

        # Remove all links.
        for input in self.node.inputs:
            for link in input.links:
                self.node.id_data.links.remove(link)

        for output in self.node.outputs:
            for link in output.links:
                self.node.id_data.links.remove(link)

        return self

    def __exit__(self, *exc: Any):
        for input in self.node.inputs:
            if input.enabled and input.name in self.inputs:
                for socket in self.inputs[input.name]:
                    self.node.id_data.links.new(socket, input)

        for output in self.node.outputs:
            if output.enabled and output.name in self.outputs:
                for socket in self.outputs[output.name]:
                    self.node.id_data.links.new(output, socket)
