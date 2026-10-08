# Wiring and power notes

## Pin map

| Pico GPIO | Connection |
|---|---|
| GP0 | I2C SDA: BNO085 + OLED |
| GP1 | I2C SCL: BNO085 + OLED |
| GP2 / GP3 | TC1508A left motor IN1 / IN2 |
| GP4 / GP5 | TC1508A right motor IN3 / IN4 |
| GP6 | BNO085 INT |
| GP7 | BNO085 RST |
| GP8–GP11 | LFS-16A S0, S1, S2, S3 |
| GP12 | Button 1: Exploration, active LOW |
| GP13 | Button 2: Final run, active LOW |
| GP14 | **Reserved and unused** |
| GP15 / GP16 | Left encoder A / B |
| GP17 / GP18 | Right encoder A / B |
| GP19–GP22 | Spare |
| GP26 / ADC0 | LFS-16A SIG through voltage divider |
| GP27 / ADC1 | Spare |
| GP28 / ADC2 | Spare |
| GP25 | Pico onboard LED |

All GPIO assignments are defined in `config.py`. GPIO numbers are not physical header pin numbers.

## LFS-16A analog safety
The LFS-16A is powered from 5 V, while the Pico ADC input range is 0–3.3 V. This project assumes SIG passes through a suitable voltage divider before GP26. **Do not connect SIG directly to GP26** until you have verified the maximum signal voltage. The correct resistor values depend on the board output range, source impedance and ADC loading; measure/verify rather than guessing.

EN is permanently tied to GND, so firmware does not control it. Mux address bit 0 maps to S0, bit 1 to S1, bit 2 to S2, bit 3 to S3.

## Power
LiPo → toggle switch → HW-133 buck and TC1508A motor supply. HW-133 is expected to provide approximately 5 V for Pico VSYS and LFS-16A, subject to the actual board's ratings. A 1000 µF capacitor is specified across the TC1508A motor supply. Verify capacitor polarity and voltage rating.

Provide common ground among Pico, sensor, motor driver, IMU, OLED and encoders. Avoid routing motor current through sensitive sensor ground paths. Check buck output with a meter before connecting the Pico.

## Driver and I2C
BNO085 INT/RST are wired to GP6/GP7, but the actual driver may require a specific reset timing and report setup. OLED and BNO085 share I2C; verify address conflicts with an I2C scan. Never assume both modules use the same voltage tolerance—confirm breakout board specifications.
