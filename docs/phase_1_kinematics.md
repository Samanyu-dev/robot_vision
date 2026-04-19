# Phase 1: 3R Robot Kinematics

## Objective

Define the 3R robot manipulator and compute the end-effector pose using standard DH transformations.

## Robot Model

The chosen robot is a simple spatial 3R arm:

- Joint 1: base yaw about the vertical axis.
- Joint 2: shoulder rotation.
- Joint 3: elbow rotation.

This keeps the model clear for visualization while still producing a true 3D pose.

## DH Parameters

Standard DH convention is used.

| Joint | theta | d | a | alpha |
| --- | --- | ---: | ---: | ---: |
| 1 | `theta_1` | `0.35 m` | `0.00 m` | `pi/2 rad` |
| 2 | `theta_2` | `0.00 m` | `0.45 m` | `0 rad` |
| 3 | `theta_3` | `0.00 m` | `0.30 m` | `0 rad` |

## Link Transform

For one link:

```text
T_i-1_i =
[ cos(theta)  -sin(theta)cos(alpha)   sin(theta)sin(alpha)   a cos(theta) ]
[ sin(theta)   cos(theta)cos(alpha)  -cos(theta)sin(alpha)   a sin(theta) ]
[     0              sin(alpha)              cos(alpha)             d     ]
[     0                   0                       0                  1     ]
```

## End-Effector Pose

The forward kinematic chain is:

```text
T_BE = T_B1 * T_12 * T_23
```

The implementation also keeps intermediate transforms:

```text
T_B0 = I
T_B1
T_B2
T_B3 = T_BE
```

These intermediate frames are needed later for:

- drawing the robot links
- drawing frame axes
- computing the geometric Jacobian
- mounting the camera on the wrist/end-effector

## Numerical Example

Using:

```text
theta_1 = 30 deg
theta_2 = 45 deg
theta_3 = -20 deg
```

The reproducible script is:

```bash
python scripts/phase1_forward_kinematics.py
```

The saved output is generated at:

```text
outputs/phase1_forward_kinematics.txt
```

For the sample angles, the end-effector position is:

```text
[0.511033, 0.295045, 0.794984] m
```

## Implementation Files

- `src/kinematics.py`
- `scripts/phase1_forward_kinematics.py`
- `tests/test_kinematics.py`
