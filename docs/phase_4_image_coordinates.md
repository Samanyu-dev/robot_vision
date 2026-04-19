# Phase 4: Image Coordinates for One Cube Vertex

## Objective

Compute the image coordinate `(u, v)` for one cube vertex using the complete chain built so far:

```text
DH kinematics -> T_BE -> T_GC -> P_C -> (u, v)
```

## Robot and Camera Setup

The sample uses the same joint angles as earlier phases:

```text
theta = [30 deg, 45 deg, -20 deg]
```

Forward kinematics gives:

```text
T_BE = T_B1 * T_12 * T_23
```

The wrist camera gives:

```text
T_GC = T_BE * T_EC
```

## Cube Vertex Setup

For this phase, one visible cube is created for the sample pose:

```text
side length = 0.20 m
cube center = 1.20 m along camera +Z_C, expressed back in world frame
selected vertex = (+L/2, +L/2, +L/2)
```

The selected vertex is then treated as a world-frame object point:

```text
P_G = [X_G, Y_G, Z_G, 1]^T
```

## Projection Steps

World to camera:

```text
P_C = inv(T_GC) * P_G
```

Perspective projection:

```text
u = fx * X_C / Z_C + cx
v = fy * Y_C / Z_C + cy
```

With:

```text
fx = 600 px
fy = 600 px
cx = 320 px
cy = 240 px
```

## Numerical Result

The reproducible script is:

```bash
python scripts/phase4_image_coordinates.py
```

The saved output is generated at:

```text
outputs/phase4_image_coordinates.txt
```

The computed pixel coordinate is:

```text
(u, v) = (336.061926, 228.642503)
```

The vertex is in front of the camera and inside the 640 x 480 image.

Detailed numerical values:

```text
P_center_G = [1.328671, 0.720921, 1.677321]^T m
P_vertex_G = [1.428671, 0.820921, 1.777321]^T m
P_vertex_C = [0.036603, -0.025882, 1.367303, 1.000000]^T m
```

## Implementation Files

- `src/cube.py`
- `scripts/phase4_image_coordinates.py`
- `tests/test_cube.py`
