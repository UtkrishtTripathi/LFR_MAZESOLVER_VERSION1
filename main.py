"""Entry point for LFR_MazeSolver on Raspberry Pi Pico / RP2040."""
import time
from machine import Pin
import config
from line_sensor import LineSensor
from motor import MotorController
from encoder import EncoderPair
from bno085 import BNO085
from odometry import Odometry
from display import StatusDisplay
from maze import Maze
from exploration import ExplorationPlanner
from controller import RobotController

class DebouncedButton:
    def __init__(self, pin_number):
        self.pin = Pin(pin_number, Pin.IN, Pin.PULL_UP)
        self.last_raw = self.pin.value()
        self.last_change = time.ticks_ms()
        self.stable = self.last_raw
        self.pressed_event = False

    def update(self):
        now = time.ticks_ms()
        raw = self.pin.value()
        if raw != self.last_raw:
            self.last_raw, self.last_change = raw, now
        if time.ticks_diff(now, self.last_change) >= config.BUTTON_DEBOUNCE_MS and raw != self.stable:
            self.stable = raw
            if self.stable == 0: self.pressed_event = True
        event, self.pressed_event = self.pressed_event, False
        return event

def main():
    motors = None
    led = Pin(config.ONBOARD_LED, Pin.OUT)
    try:
        motors = MotorController()
        sensor = LineSensor()
        encoders = EncoderPair()
        imu = BNO085()  # verified driver adapter is intentionally not guessed
        try: imu.initialize()
        except Exception as exc: print("BNO085 unavailable:", exc)
        display = StatusDisplay()  # inject actual OLED driver after selecting controller
        maze = Maze()
        planner = ExplorationPlanner(maze)
        robot = RobotController(sensor, motors, encoders, Odometry(), imu,
                               display, maze, planner)
        explore_button = DebouncedButton(config.BUTTON_EXPLORE)
        final_button = DebouncedButton(config.BUTTON_FINAL)
        display.show("READY")
        while True:
            if explore_button.update():
                if not sensor.calibrated:
                    robot.state = "CALIBRATION"
                    display.show("CALIBRATION", "Move over black/white")
                    try:
                        lo, hi = sensor.calibrate()
                        print("MIN =", lo); print("MAX =", hi)
                        display.show("CALIBRATION", "SAVED")
                    except Exception as exc:
                        robot.state = "ERROR"; robot.stop()
                        print("Calibration error:", exc)
                        display.show("ERROR", "STOPPED")
                        continue
                robot.state = "EXPLORATION"
                display.show("EXPLORE", "NODE: --")
            if final_button.update():
                if not maze.goal_id or maze.start_id is None:
                    display.show("ERROR", "NO STORED PATH")
                else:
                    from pathfinding import bfs, path_to_commands
                    robot.path = bfs(maze, maze.start_id, maze.goal_id)
                    if robot.path:
                        robot.commands = path_to_commands(maze, robot.path, 0)
                        robot.path_index = 0
                        robot.state = "FINAL_RUN"
                    else:
                        display.show("ERROR", "NO PATH")
            if robot.state in ("EXPLORATION", "FOLLOW_LINE", "FINAL_RUN", "LINE_LOST"):
                robot.control_step()
            elif robot.state in ("IDLE", "PATH_READY", "GOAL", "ERROR", "CALIBRATION", "JUNCTION", "TURNING"):
                motors.stop()
            time.sleep_ms(config.CONTROL_PERIOD_MS)
    except Exception as exc:
        if motors is not None: motors.stop()
        print("FATAL ERROR:", repr(exc))
        try:
            from display import StatusDisplay
            StatusDisplay().show("ERROR", "STOPPED")
        except Exception:
            pass
        while True:
            led.toggle()
            time.sleep_ms(250)

if __name__ == "__main__":
    main()
