"""Small MicroPython-compatible helpers."""
import time

def clamp(value, low, high):
    return low if value < low else high if value > high else value

def ticks_ms():
    return time.ticks_ms()

def elapsed_ms(start, now=None):
    if now is None:
        now = time.ticks_ms()
    return time.ticks_diff(now, start)

def mean(values):
    if not values:
        return 0.0
    return sum(values) / len(values)

def circular_heading_error(target_deg, actual_deg):
    """Signed shortest target-actual difference in degrees, range [-180, 180)."""
    return (target_deg - actual_deg + 180.0) % 360.0 - 180.0
