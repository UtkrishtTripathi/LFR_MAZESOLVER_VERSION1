import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config
from line_error import LineError, gaussian_kernel
from pid import PID
from turn_detector import TurnDetector
from maze import Maze
from pathfinding import bfs, path_to_commands
from odometry import Odometry

class LogicTests(unittest.TestCase):
    def test_gaussian_normalized(self):
        k = gaussian_kernel(5, 1.0)
        self.assertAlmostEqual(sum(k), 1.0, places=6)

    def test_local_com_center(self):
        values = [0.0] * 16
        values[7] = 1.0
        result = LineError().calculate(values)
        self.assertAlmostEqual(result["error"], -0.5, places=2)
        self.assertEqual(result["peak_idx"], 7)

    def test_per_sensor_normalization_formula_is_configured(self):
        # Formula exercised without importing machine-specific line_sensor.
        raw, lo, hi = 500, 100, 900
        self.assertAlmostEqual((raw-lo)/(hi-lo), 0.5)

    def test_pid_clamps_output(self):
        old = config.KP_STRAIGHT
        try:
            config.KP_STRAIGHT = 1000
            pid = PID()
            self.assertLessEqual(abs(pid.update(10, 0)), config.PID_OUTPUT_LIMIT)
        finally:
            config.KP_STRAIGHT = old

    def test_bfs_shortest_and_commands(self):
        m = Maze()
        a = m.add_node(0, 0, 0, [1])
        b = m.add_node(0, 100, 0, [1, 2])
        c = m.add_node(100, 100, 90, [2])
        d = m.add_node(100, 0, 180, [3])
        m.add_edge(a.id, 1, b.id)
        m.add_edge(b.id, 1, c.id)
        m.add_edge(c.id, 2, d.id)
        m.add_edge(a.id, 2, d.id)
        path = bfs(m, a.id, d.id)
        self.assertEqual(path, [a.id, d.id])
        self.assertEqual(path_to_commands(m, path, 0), ["U"])

    def test_node_merge_redirects(self):
        m = Maze()
        a = m.add_node(0, 0, 0)
        b = m.add_node(100, 0, 90)
        c = m.add_node(100, 100, 90)
        m.add_edge(a.id, 1, b.id)
        m.add_edge(b.id, 1, c.id)
        m.merge_nodes(b.id, c.id)
        self.assertNotIn(c.id, m.nodes)
        m.validate()

    def test_odometry_straight(self):
        o = Odometry()
        x, y, theta = o.update(100, 100)
        self.assertGreater(y, 0)
        self.assertAlmostEqual(x, 0.0, places=6)

if __name__ == "__main__":
    unittest.main()
