"""TC1508A dual H-bridge control. Verify driver truth table and motor polarity."""
from machine import Pin, PWM
import config
from utils import clamp

class MotorController:
    def __init__(self):
        self.pins = [
            Pin(config.LEFT_IN1, Pin.OUT), Pin(config.LEFT_IN2, Pin.OUT),
            Pin(config.RIGHT_IN1, Pin.OUT), Pin(config.RIGHT_IN2, Pin.OUT)]
        self.pwm = [PWM(p) for p in self.pins]
        for p in self.pwm: p.freq(config.MOTOR_PWM_FREQ)
        self.left_speed = self.right_speed = 0.0
        self.stop()

    def _drive(self, idx, speed, invert, trim):
        speed = clamp(speed * trim, -config.MAX_MOTOR_SPEED, config.MAX_MOTOR_SPEED)
        if invert: speed = -speed
        if abs(speed) < config.MOTOR_DEADZONE: speed = 0.0
        a, b = self.pwm[idx*2], self.pwm[idx*2+1]
        duty = int(abs(speed) * 65535 / 100.0)
        if speed > 0:
            a.duty_u16(duty); b.duty_u16(0)
        elif speed < 0:
            a.duty_u16(0); b.duty_u16(duty)
        else:
            a.duty_u16(0); b.duty_u16(0)
        return speed

    def set_left_motor(self, speed):
        self.left_speed = self._drive(0, speed, config.LEFT_MOTOR_INVERT, config.LEFT_MOTOR_TRIM)

    def set_right_motor(self, speed):
        self.right_speed = self._drive(1, speed, config.RIGHT_MOTOR_INVERT, config.RIGHT_MOTOR_TRIM)

    def set_motors(self, left_speed, right_speed):
        self.set_left_motor(left_speed); self.set_right_motor(right_speed)

    def stop(self):
        for p in self.pwm:
            p.duty_u16(0)
        self.left_speed = self.right_speed = 0.0
