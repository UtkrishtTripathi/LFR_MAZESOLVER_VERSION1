"""Hysteretic turn/straight classifier independent of junction detection."""
import config

STRAIGHT = "STRAIGHT"
TURN_LEFT = "TURN_LEFT"
TURN_RIGHT = "TURN_RIGHT"

class TurnDetector:
    def __init__(self):
        self.mode = STRAIGHT
        self.enter_count = 0
        self.exit_count = 0
        self.previous_error = 0.0

    def update(self, line):
        error = line["error"]
        peak = line["peak_idx"]
        edge = peak / 15.0
        delta = error - self.previous_error
        self.previous_error = error
        candidate = abs(error) >= config.TURN_ENTER_ERROR or (
            (edge <= config.TURN_ENTER_PEAK_EDGE or edge >= 1.0-config.TURN_ENTER_PEAK_EDGE)
            and abs(delta) >= config.TURN_ERROR_DELTA)
        if self.mode == STRAIGHT:
            self.enter_count = self.enter_count + 1 if candidate else 0
            if self.enter_count >= config.TURN_PERSISTENCE_SAMPLES:
                self.mode = TURN_LEFT if error < 0 else TURN_RIGHT
                self.enter_count = 0
        else:
            self.exit_count = self.exit_count + 1 if abs(error) <= config.TURN_EXIT_ERROR else 0
            if self.exit_count >= config.TURN_EXIT_PERSISTENCE_SAMPLES:
                self.mode = STRAIGHT
                self.exit_count = 0
            elif abs(error) > config.TURN_ENTER_ERROR:
                self.mode = TURN_LEFT if error < 0 else TURN_RIGHT
        return self.mode
