# Phase 0: System Mental Model

## Goal

Build a phase-wise simulation and analysis project that combines:

- 3R robot forward kinematics
- homogeneous coordinate transformations
- end-effector mounted camera extrinsics
- pinhole camera projection
- cube vertex projection
- Jacobian velocity analysis
- trajectory plotting
- robot and camera-view videos
- report-ready derivations, screenshots, logs, and results

## Frames

The system uses five frames:

| Frame | Meaning | Notes |
| --- | --- | --- |
| `{G}` | Global/world frame | Fixed inertial frame. |
| `{B}` | Robot base frame | Coincident with `{G}` for this project unless changed later. |
| `{E}` | End-effector/wrist frame | Computed from 3R forward kinematics. |
| `{C}` | Camera frame | Rigidly mounted to `{E}`. Uses pinhole camera coordinates. |
| `{I}` | Image frame | Pixel coordinates with origin at image top-left. |

Main point flow:

```text
P_G -> P_C -> P_I
```

## Base Assumption

For clean derivation and implementation:

```text
T_GB = I_4
T_GC = T_GB * T_BE * T_EC = T_BE * T_EC
```

This keeps the first implementation focused on the robot-camera chain. A nonzero base pose can be added later by replacing `T_GB`.

## Robot Choice

We will use a simple but spatially meaningful 3R arm:

- Joint 1 rotates about the vertical base axis.
- Joints 2 and 3 form a two-link arm after the shoulder.
- DH parameters will be implemented dynamically, not hardcoded as final matrices.

The initial DH table will be finalized in Phase 1, but the intended structure is:

| Joint | theta | d | a | alpha |
| --- | --- | --- | --- | --- |
| 1 | `theta_1` | `d1` | `a1` | `alpha_1` |
| 2 | `theta_2` | `0` | `a2` | `alpha_2` |
| 3 | `theta_3` | `0` | `a3` | `alpha_3` |

Forward kinematics:

```text
T_BE = T_01 * T_12 * T_23
```

Each transform has the homogeneous form:

```text
T = [ R  t ]
    [ 0  1 ]
```

## Camera Model

The camera is mounted rigidly on the end-effector:

```text
T_EC = [ R_tilt  t_cam ]
       [   0       1   ]
```

Camera intrinsic matrix:

```text
K = [ fx  0  cx ]
    [ 0   fy cy ]
    [ 0   0  1  ]
```

Default image plane:

```text
width  = 640 px
height = 480 px
cx     = 320 px
cy     = 240 px
```

## Projection Pipeline

Given a world point:

```text
P_G = [X_G, Y_G, Z_G, 1]^T
```

World to camera:

```text
P_C = inv(T_GC) * P_G
```

Let:

```text
P_C = [X_C, Y_C, Z_C, 1]^T
```

Perspective projection:

```text
x = X_C / Z_C
y = Y_C / Z_C
```

Pixel coordinates:

```text
u = fx * X_C / Z_C + cx
v = fy * Y_C / Z_C + cy
```

Report-ready compact equation:

```text
P_I = K * [R | t] * P_G
```

Here `[R | t]` is the world-to-camera extrinsic matrix derived from `inv(T_GC)`.

## Cube Model

The cube will be represented with 8 vertices:

```text
(+-L/2, +-L/2, +-L/2)
```

The cube can be translated to a chosen world center:

```text
P_vertex_G = P_cube_center_G + P_vertex_local
```

All vertices follow the same pipeline:

```text
P_vertex_G -> P_vertex_C -> (u, v)
```

## Image View Rules

The camera view is a 640 x 480 image.

For each projected pixel:

```text
0 <= u <= 640
0 <= v <= 480
Z_C > 0
```

If any required point is outside bounds or behind the camera, the image-view simulation will display:

```text
OBJECT OUT OF VIEW
```

## Velocity Pipeline

Forward velocity kinematics:

```text
V = J(q) * q_dot
```

For a revolute 3R manipulator:

```text
J_i = [ z_i-1 x (o_3 - o_i-1) ]
      [          z_i-1          ]
```

The full geometric Jacobian is:

```text
J = [ J_1  J_2  J_3 ]
```

If a desired end-effector spatial velocity `V` is known:

```text
q_dot = pinv(J) * V
```

The pseudoinverse is preferred for the implementation because the Jacobian is 6 x 3.

## Phase Deliverables

Each phase should produce:

- source code changes
- a log entry in `logs/`
- generated outputs when applicable
- a git commit
- a GitHub push when remote access is available

## Phase 0 Result

Phase 0 establishes:

- the frame chain
- the projection chain
- the robot/camera/cube assumptions
- the future project structure
- the GitHub dependency needed for remote push
