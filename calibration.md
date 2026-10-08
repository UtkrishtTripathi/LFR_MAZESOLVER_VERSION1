# Line sensor calibration

1. Put the robot on the real competition surface. Keep the wheels lifted or disable motor power.
2. Confirm GP26 receives SIG through a voltage divider and never exceeds 3.3 V.
3. Set `INVERT_SENSOR_VALUES = False` initially.
4. Start firmware and press Button 1. If calibration is missing/invalid, it collects `CALIBRATION_SAMPLES` samples.
5. During sampling, move the entire sensor array back and forth across the actual black line and white background. Every one of the 16 sensors must observe both colors. Do not hold it still.
6. The firmware records independent minimum and maximum values per sensor and saves `line_calibration.json`.
7. Inspect printed `MIN` and `MAX` arrays. Every channel must have a useful span; the firmware rejects a channel whose span is less than `CALIBRATION_MIN_SPAN`.
8. Use debug mode or a temporary read-only diagnostic to compare normalized values over white and black. If black is near 0 and the algorithms expect black near 1, set `INVERT_SENSOR_VALUES = True`; repeat calibration/testing after any polarity change.
9. Restart and verify calibration loads. Invalid or absent files cause calibration to be requested again.

Normalization is fixed for the run:
`(raw[i] - MIN[i]) / (MAX[i] - MIN[i])`, clamped to `[0, 1]`, optionally inverted. It is per sensor, not global. Runtime code never updates min/max. If `MAX[i] == MIN[i]`, normalization returns zero safely.

Calibration file validation checks version, list lengths, numeric values and minimum span. Keep a backup of a known-good file. Recalibrate when sensor height, lighting, surface, wiring, or sensor board changes.
