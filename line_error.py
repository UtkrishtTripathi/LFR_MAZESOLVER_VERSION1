"""Gaussian -> strongest peak -> fixed +/-2 window -> local weighted COM."""
import math
import config
from utils import clamp

def gaussian_kernel(size=None, sigma=None):
    size = config.GAUSSIAN_SIZE if size is None else size
    sigma = config.GAUSSIAN_SIGMA if sigma is None else sigma
    if size < 1 or sigma <= 0:
        raise ValueError("Gaussian size must be positive and sigma > 0")
    if size % 2 == 0:
        size += 1
    radius = size // 2
    kernel = [math.exp(-(x*x)/(2.0*sigma*sigma)) for x in range(-radius, radius+1)]
    total = sum(kernel)
    return [v / total for v in kernel]

class LineError:
    def __init__(self):
        self.kernel = gaussian_kernel()

    def smooth(self, values):
        radius = len(self.kernel) // 2
        out = [0.0] * len(values)
        for i in range(len(values)):
            acc = 0.0
            for k, weight in enumerate(self.kernel):
                src = i + k - radius
                if 0 <= src < len(values):
                    acc += values[src] * weight
            out[i] = acc
        return out

    def calculate(self, normalized):
        if len(normalized) != config.SENSOR_COUNT:
            raise ValueError("Expected 16 sensor values")
        smoothed = self.smooth(normalized)
        peak_idx = max(range(len(smoothed)), key=lambda i: smoothed[i])
        peak_value = smoothed[peak_idx]
        start = max(0, peak_idx - config.WINDOW_SIZE)
        end = min(config.SENSOR_COUNT, peak_idx + config.WINDOW_SIZE + 1)
        local_y = smoothed[start:end]
        local_pos = config.SENSOR_POSITIONS[start:end]
        denominator = sum(local_y)
        # Keep specified local COM algorithm; return neutral error if no signal.
        error = (sum(y*p for y, p in zip(local_y, local_pos)) / denominator) if denominator > 1e-9 else 0.0
        energy = sum(smoothed)
        confidence = clamp(peak_value / max(energy, 1e-9) * config.SENSOR_COUNT, 0.0, 1.0)
        lost = (peak_value < config.LINE_LOST_PEAK or energy < config.LINE_ENERGY_MIN or
                confidence < config.LINE_LOST_CONFIDENCE)
        return {"error": error, "peak_idx": peak_idx, "peak_position": config.SENSOR_POSITIONS[peak_idx],
                "peak_value": peak_value, "energy": energy, "confidence": confidence,
                "line_lost": lost, "smoothed": smoothed}
