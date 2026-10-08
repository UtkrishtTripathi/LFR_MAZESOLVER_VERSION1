"""Cycle-capable maze graph and safe duplicate-node merging."""
import math
import config
from node import Node

class Maze:
    def __init__(self):
        self.nodes = {}
        self.next_id = 0
        self.start_id = None
        self.goal_id = None

    def add_node(self, x, y, heading=0.0, available=None):
        if len(self.nodes) >= config.MAZE_MAX_NODES:
            raise RuntimeError("Maze node limit reached")
        node = Node(self.next_id, x, y, heading, available)
        self.nodes[node.id] = node
        self.next_id += 1
        if self.start_id is None: self.start_id = node.id
        return node

    def add_edge(self, a_id, direction, b_id):
        if a_id not in self.nodes or b_id not in self.nodes:
            raise KeyError("Unknown node")
        self.nodes[a_id].connect(direction, b_id)
        self.nodes[b_id].connect((direction + 2) % 4, a_id)

    def find_duplicate(self, x, y, heading, available=None):
        available = set(available or [])
        for node in self.nodes.values():
            distance = math.hypot(node.x-x, node.y-y)
            hd = abs((node.heading-heading+180.0) % 360.0 - 180.0)
            branch_match = len(node.available_directions & available)
            if (distance <= config.POSITION_TOLERANCE_MM and
                hd <= config.HEADING_TOLERANCE_DEG and
                (not available or not node.available_directions or
                 branch_match >= min(config.NODE_BRANCH_MATCH_MIN, len(available)))):
                return node
        return None

    def merge_nodes(self, keep_id, remove_id):
        if keep_id == remove_id: return self.nodes[keep_id]
        keep, remove = self.nodes[keep_id], self.nodes[remove_id]
        for direction, neighbor_id in list(remove.connections.items()):
            target_id = keep_id if neighbor_id == remove_id else neighbor_id
            if target_id != keep_id:
                keep.connections.setdefault(direction, target_id)
                if target_id in self.nodes:
                    neighbor = self.nodes[target_id]
                    for d, n in list(neighbor.connections.items()):
                        if n == remove_id: neighbor.connections[d] = keep_id
        keep.available_directions |= remove.available_directions
        keep.explored_directions |= remove.explored_directions
        keep.visited = keep.visited or remove.visited
        keep.metadata.update(remove.metadata)
        for node in self.nodes.values():
            for direction, neighbor in list(node.connections.items()):
                if neighbor == remove_id:
                    if node.id == keep_id and direction in keep.connections and keep.connections[direction] == keep_id:
                        del keep.connections[direction]
                    else:
                        node.connections[direction] = keep_id
        del self.nodes[remove_id]
        if self.start_id == remove_id: self.start_id = keep_id
        if self.goal_id == remove_id: self.goal_id = keep_id
        return keep

    def add_or_merge_node(self, x, y, heading=0.0, available=None):
        found = self.find_duplicate(x, y, heading, available)
        return found if found else self.add_node(x, y, heading, available)

    def neighbors(self, node_id):
        return [(direction, other) for direction, other in self.nodes[node_id].connections.items()
                if other in self.nodes]

    def validate(self):
        for node in self.nodes.values():
            for other in node.connections.values():
                if other not in self.nodes:
                    raise ValueError("Dangling edge from node %s" % node.id)
        return True
