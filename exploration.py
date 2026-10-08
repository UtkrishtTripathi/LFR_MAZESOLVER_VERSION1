"""Systematic graph exploration policy.

Hardware motion and branch sensing are injected by the controller. This module chooses
the next globally oriented unexplored edge and supports cycle-safe backtracking.
"""
from pathfinding import bfs

class ExplorationPlanner:
    def __init__(self, maze):
        self.maze = maze
        self.current_node_id = maze.start_id
        self.stack = []
        self.completed = False

    def observe_node(self, node_id, available_global_directions):
        node = self.maze.nodes[node_id]
        node.visited = True
        node.available_directions |= set(available_global_directions)
        self.current_node_id = node_id

    def choose_direction(self):
        node = self.maze.nodes[self.current_node_id]
        unexplored = node.unexplored_directions()
        for direction in unexplored:
            node.explored_directions.add(direction)
            self.stack.append((node.id, direction))
            return direction
        # Backtrack along an existing edge to the nearest node with unexplored exits.
        for source_id, direction in reversed(self.stack):
            if source_id in self.maze.nodes:
                source = self.maze.nodes[source_id]
                if source.unexplored_directions():
                    route = bfs(self.maze, self.current_node_id, source_id)
                    if len(route) >= 2:
                        return self.maze.nodes[route[0]].connections and self._first_direction(route)
        self.completed = True
        return None

    def _first_direction(self, route):
        if len(route) < 2: return None
        for direction, neighbor in self.maze.neighbors(route[0]):
            if neighbor == route[1]: return direction
        return None

    def record_traversal(self, from_id, direction, to_id):
        self.maze.add_edge(from_id, direction, to_id)
        self.current_node_id = to_id
        if self.stack and self.stack[-1] == (from_id, direction):
            self.stack.pop()
