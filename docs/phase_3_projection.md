# Phase 3: Projection Derivation

## Objective

Derive and implement the world-to-image mapping:

```text
P_I = K * [R | t] * P_G
```

This is the report-critical projection phase.

## Intrinsic Matrix

The pinhole camera intrinsic matrix is:

```text
K = [ fx  0  cx ]
    [ 0   fy cy ]
    [ 0   0  1  ]
```

Default values:

```text
fx = 600 px
fy = 600 px
cx = 320 px
cy = 240 px
image size = 640 x 480 px
```

## Extrinsic Matrix

Phase 2 produced the camera pose in the global frame:

```text
T_GC = T_GB * T_BE * T_EC
```

With the base at the global origin:

```text
T_GC = T_BE * T_EC
```

To transform a world point into the camera frame:

```text
P_C = inv(T_GC) * P_G
```

The world-to-camera extrinsic matrix is the first three rows of `inv(T_GC)`:

```text
[R | t] = inv(T_GC)[0:3, :]
```

## Perspective Projection

Let:

```text
P_C = [X_C, Y_C, Z_C, 1]^T
```

Normalized image-plane coordinates:

```text
x = X_C / Z_C
y = Y_C / Z_C
```

Pixel coordinates:

```text
u = fx * X_C / Z_C + cx
v = fy * Y_C / Z_C + cy
```

Compact matrix form:

```text
s * [u, v, 1]^T = K * [R | t] * P_G
```

where `s = Z_C`.

## Numerical Example

The reproducible script is:

```bash
python scripts/phase3_projection.py
```

The saved output is generated at:

```text
outputs/phase3_projection.txt
```

The sample point is chosen in front of the camera:

```text
P_C = [0.05, -0.03, 1.00, 1.00]^T
```

It is converted to world coordinates using:

```text
P_G = T_GC * P_C
```

For the current sample pose:

```text
P_G = [1.199568, 0.704118, 1.514687, 1.000000]^T
```

Then projected back through:

```text
P_C = inv(T_GC) * P_G
```

The expected pixel coordinate is:

```text
u = 600 * 0.05 / 1.00 + 320 = 350 px
v = 600 * -0.03 / 1.00 + 240 = 222 px
```

So:

```text
(u, v) = (350, 222)
```

## Planned UI Viewer

A lightweight UI will be added in a later visualization phase after cube projection is implemented. The intended controls are:

- joint sliders for `theta_1`, `theta_2`, and `theta_3`
- a 3D robot/camera/cube view
- a 640 x 480 camera-image view
- an out-of-view indicator

## Implementation Files

- `src/projection.py`
- `scripts/phase3_projection.py`
- `tests/test_projection.py`
