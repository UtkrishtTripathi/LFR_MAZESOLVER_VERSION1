"""Single PID controller with selectable straight/turn gains and anti-windup."""
import config
from utils import clamp

class PID:
    def __init__(self):
        self.integral = 0.0
        self.previous_error = None
        self.previous_time = None
        self.output = 0.0
        self.mode = "STRAIGHT"

    def reset(self):
        self.integral = 0.0
        self.previous_error = None
        self.previous_time = None
        self.output = 0.0

    def set_mode(self, mode):
        if mode != self.mode:
            self.mode = mode
            self.reset()

    def update(self, error, now_ms, mode="STRAIGHT"):
        self.set_mode(mode)
        kp, ki, kd = ((config.KP_TURN, config.KI_TURN, config.KD_TURN)
                      if mode == "TURN" else
                      (config.KP_STRAIGHT, config.KI_STRAIGHT, config.KD_STRAIGHT))
        if self.previous_time is None:
            dt = config.CONTROL_PERIOD_MS / 1000.0
        else:
            import time
            dt = time.ticks_diff(now_ms, self.previous_time) / 1000.0
        dt = max(0.001, min(dt, 0.1))
        derivative = 0.0 if self.previous_error is None else (error - self.previous_error) / dt
        proposed = clamp(self.integral + error * dt, -config.PID_INTEGRAL_LIMIT, config.PID_INTEGRAL_LIMIT)
        raw = kp * error + ki * proposed + kd * derivative
        output = clamp(raw, -config.PID_OUTPUT_LIMIT, config.PID_OUTPUT_LIMIT)
        # Integrate only if not pushing farther into saturation.
        if raw == output or (raw > output and error < 0) or (raw < output and error > 0):
            self.integral = proposed
        self.previous_error, self.previous_time, self.output = error, now_ms, output
        return output
