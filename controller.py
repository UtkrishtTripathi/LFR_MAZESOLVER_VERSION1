"""High-level robot controller and independent junction/goal state machines."""
import time
import config
from pid import PID
from turn_detector import TurnDetector, STRAIGHT
from line_error import LineError
from utils import clamp

class JunctionDetector:
    """Pattern-based junction detector with confirm and leave lock."""
    def __init__(self):
        self.state = "ARMED"
        self.confirm_count = 0
        self.clear_count = 0

    def classify(self, values):
        left = max(values[:5]) >= config.JUNCTION_SIDE_THRESHOLD
        right = max(values[11:]) >= config.JUNCTION_SIDE_THRESHOLD
        center = max(values[5:11]) >= config.JUNCTION_CENTER_THRESHOLD
        active = sum(1 for v in values if v >= config.JUNCTION_ACTIVE_THRESHOLD)
        if active >= config.GOAL_BLACK_SENSOR_COUNT:
            return "GOAL"
        if active < config.JUNCTION_MIN_ACTIVE_SENSORS:
            return "NONE"
        if left and right and center: return "CROSS"
        if left and right: return "T"
        if left and center: return "LEFT_STRAIGHT"
        if right and center: return "RIGHT_STRAIGHT"
        if left: return "LEFT"
        if right: return "RIGHT"
        if center: return "STRAIGHT"
        return "DEAD_END"

    def update(self, values):
        pattern = self.classify(values)
        active = sum(1 for v in values if v >= config.JUNCTION_ACTIVE_THRESHOLD)
        if self.state == "ARMED":
            if pattern not in ("NONE", "STRAIGHT", "GOAL"):
                self.confirm_count += 1
                if self.confirm_count >= config.JUNCTION_CONFIRM_SAMPLES:
                    self.state = "LOCKED"
                    self.confirm_count = 0
                    return "CONFIRMED", pattern
            else:
                self.confirm_count = 0
        else:
            if active <= 2:
                self.clear_count += 1
                if self.clear_count >= config.JUNCTION_CLEAR_SAMPLES:
                    self.state = "ARMED"
                    self.clear_count = 0
            else:
                self.clear_count = 0
        return "NONE", pattern

class RobotController:
    def __init__(self, line_sensor, motors, encoders, odometry, imu, display, maze, planner):
        self.sensor, self.motors, self.encoders = line_sensor, motors, encoders
        self.odometry, self.imu, self.display = odometry, imu, display
        self.maze, self.planner = maze, planner
        self.pid = PID()
        self.line_error = LineError()
        self.turn_detector = TurnDetector()
        self.junction = JunctionDetector()
        self.state = "IDLE"
        self.last_error = 0.0
        self.line_lost_since = None
        self.goal_since = None
        self.path = []
        self.path_index = 0
        self.current_node = None
        self.last_debug = 0

    def stop(self):
        self.motors.stop()
        self.pid.reset()

    def _goal_check(self, normalized, now):
        count = sum(1 for v in normalized if v >= config.JUNCTION_ACTIVE_THRESHOLD)
        if count >= config.GOAL_BLACK_SENSOR_COUNT:
            if self.goal_since is None: self.goal_since = now
            if time.ticks_diff(now, self.goal_since) >= config.GOAL_CONFIRM_MS:
                self.state = "GOAL"; self.stop()
                self.display.show("GOAL", "PATH COMPLETE")
                return True
        else:
            self.goal_since = None
        return False

    def control_step(self):
        now = time.ticks_ms()
        raw, normalized = self.sensor.read()
        line = self.line_error.calculate(normalized)
        if self._goal_check(normalized, now): return
        self.last_error = line["error"]
        if self.state in ("IDLE", "GOAL", "ERROR", "PATH_READY"):
            self.stop(); return
        if line["line_lost"]:
            if self.line_lost_since is None: self.line_lost_since = now
            self.state = "LINE_LOST"
            if time.ticks_diff(now, self.line_lost_since) > config.LINE_RECOVERY_TIMEOUT_MS:
                raise RuntimeError("Line recovery timeout")
            direction = -1 if self.last_error < 0 else 1
            self.motors.set_motors(config.BASE_SPEED_SEARCH * direction,
                                   -config.BASE_SPEED_SEARCH * direction)
            self.display.show("LINE LOST", "RECOVERING")
            return
        if self.state == "LINE_LOST":
            self.line_lost_since = None
            self.pid.reset()
            self.state = "FOLLOW_LINE"
        turn = self.turn_detector.update(line)
        junction_event, pattern = self.junction.update(normalized)
        if junction_event == "CONFIRMED":
            self.state = "JUNCTION"
            self.stop()
            self.display.show("JUNCTION", pattern)
            # Competition-specific traversal/turn execution is delegated to the
            # mission layer; stop here rather than inventing physical turn timing.
            return
        mode = "TURN" if turn != STRAIGHT else "STRAIGHT"
        base = config.BASE_SPEED_TURN if mode == "TURN" else config.BASE_SPEED_STRAIGHT
        correction = self.pid.update(line["error"], now, mode)
        self.motors.set_motors(clamp(base + correction, -100, 100),
                               clamp(base - correction, -100, 100))
        if config.DEBUG and time.ticks_diff(now, self.last_debug) >= config.DEBUG_PERIOD_MS:
            self.last_debug = now
            print("raw=", raw, "norm=", normalized, "peak=", line["peak_idx"],
                  "confidence=", line["confidence"], "error=", line["error"],
                  "turn=", turn, "pid=", self.pid.output, "motors=",
                  self.motors.left_speed, self.motors.right_speed)
