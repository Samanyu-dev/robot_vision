# Phase 2: Camera Extrinsics

## Objective

Mount a camera on the end-effector and compute the camera pose in the global frame.

## Camera Mount

The camera is rigidly attached to the wrist/end-effector frame:

```text
T_EC = [ R_EC  t_EC ]
      [  0      1   ]
```

For this project:

```text
t_EC = [0.08, 0.00, 0.04]^T m
tilt = -20 deg about the local camera x-axis
```

The alignment rotation makes the optical axis `+Z_C` point along end-effector forward `+X_E`:

```text
R_EC = R_y(pi/2) * R_x(tilt)
```

## World to Camera Pose

The complete chain is:

```text
T_GC = T_GB * T_BE * T_EC
```

With the base at the global origin:

```text
T_GB = I
T_GC = T_BE * T_EC
```

This gives the camera frame pose relative to the global frame.

## Numerical Example

Using the same robot pose from Phase 1:

```text
theta_1 = 30 deg
theta_2 = 45 deg
theta_3 = -20 deg
```

The reproducible script is:

```bash
python scripts/phase2_camera_extrinsics.py
```

The saved output is generated at:

```text
outputs/phase2_camera_extrinsics.txt
```

For the sample angles, the computed camera origin is:

```text
[0.593824, 0.296656, 0.828793] m
```

The optical axis `+Z_C` in the global/base frame is:

```text
[0.612372, 0.353553, 0.707107]
```

## Report Notes

The camera pose matrix `T_GC` is not yet the projection matrix. Phase 3 will invert `T_GC` to transform world points into the camera frame:

```text
P_C = inv(T_GC) * P_G
```

Then the pinhole model will project `P_C` into the image plane.

## Implementation Files

- `src/camera.py`
- `scripts/phase2_camera_extrinsics.py`
- `tests/test_camera.py`
