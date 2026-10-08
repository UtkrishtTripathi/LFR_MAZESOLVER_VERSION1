# Tuning guide

Tune with the robot lifted first, then at low speed on a short straight track. Change one setting at a time.

## 1. Confirm signs and sensor polarity
- Verify sensor values clearly distinguish black and white.
- Verify line error sign: positions left of center are negative and right are positive in `SENSOR_POSITIONS`.
- Verify motor command signs on the chassis. If forward commands reverse a motor, change that motor's `*_MOTOR_INVERT`.

## 2. Gaussian filter and line confidence
- `GAUSSIAN_SIZE` should be an odd number; `GAUSSIAN_SIGMA` controls smoothing.
- More smoothing reduces noise but can blur close branches.
- `LINE_LOST_PEAK`, `LINE_ENERGY_MIN`, and `LINE_LOST_CONFIDENCE` must be tested on real line, white floor and junctions. Do not loosen them so far that a missing line appears valid.

## 3. PID
The same PID object selects one gain set:
- straight: `KP_STRAIGHT`, `KI_STRAIGHT`, `KD_STRAIGHT`
- turn: `KP_TURN`, `KI_TURN`, `KD_TURN`

Start with KI at zero. Increase KP until tracking is responsive but begins to oscillate, then back off. Add a small KD to damp oscillation. Add KI only if a repeatable steady bias remains. Integral and output clamps are configurable. Tune at conservative `BASE_SPEED_STRAIGHT` and `BASE_SPEED_TURN` first.

## 4. Turn detector
`TURN_ENTER_ERROR` and `TURN_EXIT_ERROR` provide hysteresis. Enter threshold should exceed exit threshold. Persistence counts suppress single-sample switching. Peak-edge and error-change thresholds supplement error magnitude.

## 5. Junction and goal thresholds
The junction detector uses the 16-sensor pattern and active-sensor count, not line error alone. Adjust side/center/active thresholds from recorded patterns for straight, T, cross, dead-end and goal. `JUNCTION_CONFIRM_SAMPLES` and `JUNCTION_CLEAR_SAMPLES` control debounce/lock. Goal confirmation is separate and starts at 250 ms; tune within roughly 100–500 ms.

## 6. Motion and encoders
Measure wheel diameter under load and wheel base between wheel contact centerlines. Confirm whether encoder CPR is specified per motor shaft or wheel shaft, and whether it counts one edge, both edges, or full x4 quadrature. Set `ENCODER_COUNTS_PER_REV` and `ENCODER_QUADRATURE_MULTIPLIER` consistently. Verify straight-line odometry and 90-degree turns before using mapped coordinates.

## 7. Competition-specific maneuvers
Do not tune a blind fixed-delay turn without testing the actual chassis. Implement node arrival, branch availability sensing, turn execution, line reacquisition, and graph edge recording in the mission layer before running autonomously.
