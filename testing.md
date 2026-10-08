# Testing and bring-up checklist

## Desktop logic tests
From the project directory with Python 3:
`python -m unittest discover -s tests -v`

These tests cover pure logic only. They do not validate Pico electrical behavior, motor driver polarity, sensor calibration, or actual maze driving.

## Safe hardware sequence
1. With motor supply disconnected, verify all wiring and buck output.
2. Confirm divider output stays below 3.3 V across black/white readings.
3. Boot Pico with wheels off the ground. Confirm motor PWM starts at zero.
4. Test each motor direction at low duty. Verify `stop()` sets all four PWM duties to zero.
5. Inspect all 16 raw mux channels one by one; compare against a multimeter where useful.
6. Calibrate over both black and white.
7. Check normalized line values, Gaussian peak and local COM error at center and both sides.
8. Test line-lost recovery on white floor; it must time out to a safe stop.
9. Check encoder count direction and counts over a measured wheel rotation.
10. Verify odometry with a measured straight roll and a 90-degree turn.
11. Verify I2C addresses and integrate verified OLED/BNO085 drivers.
12. Test junction detection on each known pattern; confirm it stays locked until the robot leaves.
13. Test node merge and BFS on a small graph with a loop.
14. Test goal confirmation with a black square and verify it cancels if the black pattern disappears.
15. Only then test slow exploration, then final path.

## Logic-test limits
The host tests use a fake/simple object model where possible. Hardware modules import `machine` and must run on MicroPython or under a hardware stub. A passing desktop test is not proof of safe real-world behavior.
