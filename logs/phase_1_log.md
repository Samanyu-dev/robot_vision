# Phase 1 Log

Date: 2026-04-19

## Objective

Implement the 3R manipulator forward kinematics using standard DH parameters.

## Completed

- Added `src/kinematics.py`.
- Implemented:

```text
dh_transform(theta, d, a, alpha)
forward_kinematics(joint_angles)
end_effector_position(joint_angles)
```

- Selected a spatial 3R arm with:

```text
d1 = 0.35 m
a1 = 0.00 m
alpha1 = pi/2 rad
a2 = 0.45 m
a3 = 0.30 m
```

- Added a reproducible numerical example script.
- Added unit tests for DH transform shape, zero-pose position, helper consistency, and input validation.

## Expected Numerical Example

The script uses:

```text
theta = [30 deg, 45 deg, -20 deg]
```

It prints:

- DH table
- joint angles
- `T_B1`
- `T_B2`
- `T_B3`
- final `T_BE`
- end-effector position

The generated end-effector position is:

```text
[0.511033 0.295045 0.794984] m
```

## Verification

Created a project virtual environment and installed dependencies from `requirements.txt`.

Commands run:

```text
.venv/bin/python scripts/phase1_forward_kinematics.py
.venv/bin/python -m unittest discover -s tests
```

Result:

```text
Ran 5 tests in 0.013s
OK
```

## Next Phase

Phase 2 will add the camera extrinsic transform:

```text
T_EC = [R_tilt  t_cam]
      [  0       1   ]
```

Then compute:

```text
T_GC = T_BE * T_EC
```
