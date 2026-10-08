"""BNO085 adapter boundary.

No concrete BNO085 MicroPython API is assumed here. Install/port a verified driver
for the exact sensor breakout and implement _read_heading_degrees() below.
Heading convention used by this project: degrees clockwise from global NORTH,
normalized to [0, 360). Verify sensor mounting and remap axes in the adapter.
"""
from machine import Pin, I2C
import config

class BNO085:
    def __init__(self, driver=None):
        self.i2c = I2C(config.I2C_ID, sda=Pin(config.I2C_SDA), scl=Pin(config.I2C_SCL),
                       freq=config.I2C_FREQ)
        self.int_pin = Pin(config.BNO085_INT, Pin.IN, Pin.PULL_UP)
        self.rst_pin = Pin(config.BNO085_RST, Pin.OUT)
        self.driver = driver
        self.available = False
        self.last_heading = None
        if driver is not None:
            self.available = True

    def initialize(self):
        if self.driver is None:
            self.available = False
            return False
        # Driver initialization is intentionally delegated to verified adapter.
        self.driver.initialize(self.i2c, self.int_pin, self.rst_pin)
        self.available = True
        return True

    def _read_heading_degrees(self):
        """TODO: implement using the selected, verified BNO085 driver/report."""
        if self.driver is None:
            return None
        return self.driver.heading_degrees()

    def heading(self):
        try:
            value = self._read_heading_degrees()
            if value is not None:
                self.last_heading = float(value) % 360.0
        except Exception:
            self.available = False
        return self.last_heading

    def reset(self):
        self.rst_pin.value(0)
        import time
        time.sleep_ms(10)
        self.rst_pin.value(1)
