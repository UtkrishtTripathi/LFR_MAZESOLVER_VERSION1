"""LFS-16A mux reader and fixed per-sensor calibration/normalization."""
import time
import json
from machine import Pin, ADC
import config
from utils import clamp

class LineSensor:
    def __init__(self):
        self.select = [
            Pin(config.MUX_S0, Pin.OUT), Pin(config.MUX_S1, Pin.OUT),
            Pin(config.MUX_S2, Pin.OUT), Pin(config.MUX_S3, Pin.OUT)]
        self.adc = ADC(Pin(config.ADC_LINE))
        self.minimum = list(range(config.SENSOR_COUNT))
        self.maximum = list(range(config.SENSOR_COUNT))
        self.calibrated = False
        self.last_raw = [0] * config.SENSOR_COUNT
        self.last_normalized = [0.0] * config.SENSOR_COUNT
        self.load_calibration()

    def read_channel(self, channel):
        for bit, pin in enumerate(self.select):
            pin.value((channel >> bit) & 1)
        time.sleep_us(8)  # mux settling; tune after checking scope/readings
        # Discard first conversion after switching channels.
        self.adc.read_u16()
        return self.adc.read_u16()

    def read_raw(self):
        values = [self.read_channel(i) for i in range(config.SENSOR_COUNT)]
        self.last_raw = values
        return values

    def normalize(self, raw):
        out = []
        for i, value in enumerate(raw):
            lo, hi = self.minimum[i], self.maximum[i]
            span = hi - lo
            n = 0.0 if span <= 0 else (value - lo) / span
            n = clamp(n, 0.0, 1.0)
            if config.INVERT_SENSOR_VALUES:
                n = 1.0 - n
            out.append(n)
        self.last_normalized = out
        return out

    def read(self):
        raw = self.read_raw()
        return raw, self.normalize(raw)

    def calibrate(self, samples=config.CALIBRATION_SAMPLES, progress=None):
        """Collect samples while user moves the array across expected white and black."""
        lo = [65535] * config.SENSOR_COUNT
        hi = [0] * config.SENSOR_COUNT
        for sample_idx in range(samples):
            values = self.read_raw()
            for i, value in enumerate(values):
                if value < lo[i]: lo[i] = value
                if value > hi[i]: hi[i] = value
            if progress and sample_idx % 20 == 0:
                progress(sample_idx, samples)
            time.sleep_ms(config.CALIBRATION_SAMPLE_DELAY_MS)
        # Reject nearly flat channels rather than pretending they calibrated correctly.
        for i in range(config.SENSOR_COUNT):
            if hi[i] - lo[i] < config.CALIBRATION_MIN_SPAN:
                raise ValueError("Sensor %d calibration span too small (%d)" %
                                 (i, hi[i] - lo[i]))
        self.minimum, self.maximum = lo, hi
        self.calibrated = True
        self.save_calibration()
        return lo[:], hi[:]

    def save_calibration(self):
        payload = {"version": 1, "minimum": self.minimum, "maximum": self.maximum}
        with open(config.CALIBRATION_FILE, "w") as f:
            json.dump(payload, f)

    def load_calibration(self):
        try:
            with open(config.CALIBRATION_FILE, "r") as f:
                data = json.load(f)
            lo, hi = data["minimum"], data["maximum"]
            if data.get("version") != 1 or len(lo) != config.SENSOR_COUNT or len(hi) != config.SENSOR_COUNT:
                return
            if any(not isinstance(v, (int, float)) for v in lo + hi):
                return
            if any(hi[i] - lo[i] < config.CALIBRATION_MIN_SPAN for i in range(config.SENSOR_COUNT)):
                return
            self.minimum, self.maximum = list(lo), list(hi)
            self.calibrated = True
        except (OSError, ValueError, KeyError, TypeError):
            self.calibrated = False
