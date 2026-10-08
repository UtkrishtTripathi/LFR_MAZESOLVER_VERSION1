"""Differential-drive odometry using wheel encoders; optional heading correction."""
import math
import config

class Odometry:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0  # radians, zero points NORTH; clockwise positive
        self.left_mm_per_count = math.pi * config.WHEEL_DIAMETER_MM / (
            config.ENCODER_COUNTS_PER_REV * config.ENCODER_QUADRATURE_MULTIPLIER)
        self.right_mm_per_count = self.left_mm_per_count

    def update(self, left_delta, right_delta, imu_heading_deg=None):
        dl = left_delta * self.left_mm_per_count
        dr = right_delta * self.right_mm_per_count
        distance = (dl + dr) / 2.0
        dtheta = (dr - dl) / config.WHEEL_BASE_MM
        self.theta += dtheta
        if imu_heading_deg is not None:
            target = math.radians(imu_heading_deg)
            # Blend encoder yaw with IMU heading, avoiding accelerometer integration.
            diff = (target - self.theta + math.pi) % (2.0 * math.pi) - math.pi
            self.theta += config.ODOMETRY_HEADING_CORRECTION * diff
        # x east, y north; clockwise-positive theta from north.
        self.x += distance * math.sin(self.theta)
        self.y += distance * math.cos(self.theta)
        return self.x, self.y, self.theta
