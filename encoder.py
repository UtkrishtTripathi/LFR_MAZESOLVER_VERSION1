"""Interrupt-driven quadrature encoders. ISR only updates integer counters."""
from machine import Pin
import config

class QuadratureEncoder:
    # Gray-code transition table; invalid two-bit jumps contribute zero.
    _TABLE = (0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0)
    def __init__(self, pin_a, pin_b, invert=False):
        self.a = Pin(pin_a, Pin.IN, Pin.PULL_UP)
        self.b = Pin(pin_b, Pin.IN, Pin.PULL_UP)
        self.count = 0
        self.previous = (self.a.value() << 1) | self.b.value()
        self.invert = invert
        self.a.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._irq)
        self.b.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._irq)

    def _irq(self, pin):
        current = (self.a.value() << 1) | self.b.value()
        delta = self._TABLE[(self.previous << 2) | current]
        self.count += -delta if self.invert else delta
        self.previous = current

    def read(self):
        return self.count

    def delta(self, previous_count):
        return self.count - previous_count

    def reset(self):
        self.count = 0
        self.previous = (self.a.value() << 1) | self.b.value()

class EncoderPair:
    def __init__(self):
        self.left = QuadratureEncoder(config.ENC_LEFT_A, config.ENC_LEFT_B)
        self.right = QuadratureEncoder(config.ENC_RIGHT_A, config.ENC_RIGHT_B)
        self._last_left = self.left.read()
        self._last_right = self.right.read()

    def counts(self):
        return self.left.read(), self.right.read()

    def delta_counts(self):
        left, right = self.counts()
        dl, dr = left - self._last_left, right - self._last_right
        self._last_left, self._last_right = left, right
        return dl, dr

    def reset(self):
        self.left.reset(); self.right.reset()
        self._last_left = self._last_right = 0
