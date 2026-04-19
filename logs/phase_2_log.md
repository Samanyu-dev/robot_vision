# Phase 2 Log

Date: 2026-04-19

## Objective

Add the rigid camera transform mounted on the end-effector and compute:

```text
T_GC = T_BE * T_EC
```

## Completed

- Added `src/camera.py`.
- Implemented:

```text
rotation_x(angle_rad)
rotation_y(angle_rad)
homogeneous_transform(rotation, translation)
camera_mount_transform(mount)
camera_pose_from_end_effector(end_effector_transform, camera_transform_e_c)
camera_pose_in_global(joint_angles, mount)
```

- Defined default camera mount:

```text
t_EC = [0.08, 0.00, 0.04]^T m
tilt = -20 deg about local camera x-axis
```

- Used this rotation convention:

```text
R_EC = R_y(pi/2) * R_x(tilt)
```

This maps camera optical axis `+Z_C` along end-effector forward `+X_E`, with fixed tilt.

## Expected Numerical Example

The script uses:

```text
theta = [30 deg, 45 deg, -20 deg]
```

It prints:

- joint angles
- camera translation and tilt
- `T_BE`
- `T_EC`
- `T_GC`
- camera origin in global/base frame
- camera optical axis in global/base frame

The generated camera origin is:

```text
[0.593824 0.296656 0.828793] m
```

The generated camera optical axis `+Z_C` in the global/base frame is:

```text
[0.612372 0.353553 0.707107]
```

## Verification

Commands run:

```text
.venv/bin/python scripts/phase2_camera_extrinsics.py
.venv/bin/python -m unittest discover -s tests
```

Result:

```text
Ran 11 tests in 0.014s
OK
```

## Next Phase

Phase 3 will derive and implement the projection equation:

```text
P_C = inv(T_GC) * P_G
u = fx * X_C / Z_C + cx
v = fy * Y_C / Z_C + cy
```
