def node_location_absolute(node):
    if node.parent:
        return node.location.copy() + node_location_absolute(node.parent)
    else:
        return node.location.copy()
