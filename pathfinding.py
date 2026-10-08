"""BFS shortest path for equal-cost graph edges and global-to-relative commands."""
from collections import deque

def bfs(maze, start_id, goal_id):
    if start_id not in maze.nodes or goal_id not in maze.nodes:
        return []
    queue = deque([start_id])
    parent = {start_id: None}
    while queue:
        current = queue.popleft()
        if current == goal_id: break
        for _, neighbor in maze.neighbors(current):
            if neighbor not in parent:
                parent[neighbor] = current
                queue.append(neighbor)
    if goal_id not in parent: return []
    path, cur = [], goal_id
    while cur is not None:
        path.append(cur); cur = parent[cur]
    return list(reversed(path))

def direction_between(maze, from_id, to_id):
    for direction, neighbor in maze.nodes[from_id].connections.items():
        if neighbor == to_id: return direction
    raise ValueError("Path contains non-connected nodes")

def path_to_commands(maze, node_path, start_heading):
    """Commands L/R/S/U; headings use N=0,E=1,S=2,W=3 clockwise."""
    commands = []
    heading = int(round(start_heading / 90.0)) % 4
    for a, b in zip(node_path, node_path[1:]):
        direction = direction_between(maze, a, b)
        relative = (direction - heading) % 4
        commands.append(("S", "R", "U", "L")[relative])
        heading = direction
    return commands
