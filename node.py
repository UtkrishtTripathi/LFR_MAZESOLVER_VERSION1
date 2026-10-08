"""Maze node with globally oriented connections."""
import config

class Node:
    def __init__(self, node_id, x, y, heading=0.0, available=None):
        self.id = node_id
        self.x, self.y = float(x), float(y)
        self.heading = float(heading) % 360.0
        self.connections = {}  # global direction integer -> neighbor node id
        self.explored_directions = set()
        self.available_directions = set(available or [])
        self.visited = False
        self.metadata = {}

    def connect(self, direction, other_id):
        self.connections[int(direction) % 4] = other_id

    def unexplored_directions(self):
        return [d for d in sorted(self.available_directions)
                if d not in self.explored_directions]

    def as_dict(self):
        return {"id": self.id, "x": self.x, "y": self.y, "heading": self.heading,
                "connections": self.connections, "explored": list(self.explored_directions),
                "available": list(self.available_directions), "visited": self.visited,
                "metadata": self.metadata}
