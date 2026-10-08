# LFR_MazeSolver

Modular MicroPython starting project for a differential-drive Raspberry Pi Pico (RP2040) line-following maze robot.

> **Hardware integration status:** The control and graph logic is implemented, but this is not a plug-and-play competition-ready autonomous solver until you verify motor-driver truth table, encoder scale, line polarity, and add the real BNO085/OLED driver adapters and mission-specific junction traversal. The firmware deliberately does not guess unavailable hardware APIs.

## Features
- 16-channel LFS-16A mux readout and per-sensor fixed MIN/MAX normalization.
- Required Gaussian smoothing → strongest peak → ±2 sensor window → local weighted center-of-mass error.
- Confidence/energy-based line-loss detection.
- One PID with STRAIGHT and TURN gain sets; turn hysteresis.
- PWM motor output, quadrature encoder counters, differential odometry.
- BNO085 interface boundary, global-direction graph, duplicate-node merge, BFS, L/R/S/U conversion.
- Pattern-based junction detector with confirmation/leave lock and goal-black timer.
- Debounced GP12 exploration and GP13 final-run buttons. GP14 is intentionally untouched.
- Safety stop on fatal exceptions and line-recovery timeout.

## Pinout
See [wiring.md](wiring.md). All GPIO assignments are in `config.py`.

## Install on Pico
1. Install a current stable MicroPython UF2 for **Raspberry Pi Pico / RP2040**, not Pico W, from the official MicroPython download page.
2. Connect the Pico by USB and open Thonny or another MicroPython file tool.
3. Copy all top-level `.py` files to the Pico filesystem. Do not copy `tests/` to the Pico.
4. Select and install the correct OLED and BNO085 drivers, then implement/inject them as described in `bno085.py` and `display.py`.
5. Keep wheels off the ground for first power-up. Confirm `stop()` produces zero PWM and that motor direction is correct.
6. Follow [calibration.md](calibration.md), then [tuning.md](tuning.md).
7. Run bench tests in [testing.md](testing.md) before a competition run.

## Architecture
- `line_sensor.py`: mux and calibration file.
- `line_error.py`: exact mandated line-position algorithm.
- `turn_detector.py`: straight/turn classification with hysteresis.
- `pid.py`, `motor.py`: control and H-bridge output.
- `encoder.py`, `odometry.py`, `bno085.py`: motion feedback and IMU adapter.
- `node.py`, `maze.py`, `exploration.py`, `pathfinding.py`: graph mapping, exploration policy, BFS route.
- `controller.py`: line-following, line-loss, junction and goal state logic.
- `display.py`: rate-limited OLED facade.
- `main.py`: button handling and safe top-level loop.

## Calibration
Press Button 1 to start calibration if no valid saved calibration exists. During the sample period, move the sensor array across the actual white floor and black line, making sure every sensor sees both. Values are saved in `line_calibration.json`. Details: [calibration.md](calibration.md).

Calibration polarity is not assumed. `INVERT_SENSOR_VALUES` determines whether normalized black values are high or low. Determine it from live readings and set it before competition. The current calibration routine captures extrema across the movement; do not use a stationary array.

## PID tuning
Read [tuning.md](tuning.md). Begin with low speed, `KI_* = 0`, and adjust one parameter at a time.

## Exploration and BFS
The graph stores nodes and edges in global NORTH/EAST/SOUTH/WEST directions. The exploration policy prioritizes unexplored exits and can use known graph routes to backtrack. Loops are represented as graph cycles. BFS finds a minimum-edge path for equal-cost edges. `path_to_commands()` translates global edge directions into L/R/S/U based on heading.

**Competition integration still required:** the controller currently confirms a junction and safely stops. A robot-specific maneuver layer must identify/measure the physical node, map available global branches, execute the selected turn, reacquire the line, and call `record_traversal()`. It is safer to leave this explicit than to fabricate a turn routine without your robot's geometry and sensor placement. Likewise, final-run junction execution must consume a command only after a maneuver completes.

## Final run and goal
Button 2 is assigned to final run. The framework computes BFS if a valid graph goal has been recorded. Goal detection requires at least `GOAL_BLACK_SENSOR_COUNT` normalized channels above the active threshold for `GOAL_CONFIRM_MS`; it stops motors and reports GOAL. The maze goal node must be assigned by the competition-specific node/goal logic.

## Troubleshooting
- **Always line lost:** inspect raw values, check divider, tune thresholds and polarity.
- **Wrong turn direction:** check `SENSOR_POSITIONS`, motor inversion, and the sign convention on the chassis.
- **Encoder counts backwards/noisy:** swap A/B or configure inversion; keep wiring short and grounded.
- **OLED blank:** confirm controller (SSD1306 vs SH1106), I2C address and driver.
- **BNO085 unavailable:** select a verified MicroPython driver and implement the adapter.
- **Pico resets when motors start:** check supply capacity, common ground, motor suppression and wiring; separate noisy motor current from logic supply.
- **Robot moves at boot:** remove wheels from floor; verify H-bridge input polarity and stop behavior before enabling movement.

## Safety
- SIG is 5 V-domain hardware: **never connect it directly to Pico ADC** unless you have verified it cannot exceed 3.3 V. This design assumes an appropriately engineered voltage divider; choose and verify resistor values from the actual signal range and ADC loading.
- Share ground as required, but route motor current away from sensor/logic grounds.
- Confirm TC1508A input truth table and whether zero duty is coast or brake on your module.
- A watchdog is disabled by default; enable only after testing watchdog reset and safe motor states.
- Competition rules and field dimensions override assumptions in this template.
