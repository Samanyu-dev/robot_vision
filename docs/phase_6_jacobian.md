# Phase 6: Geometric Jacobian

## Objective

Derive and implement the 6 x 3 geometric Jacobian for the 3R arm and use it to estimate joint velocities for a desired spatial velocity.

## Definition

For revolute joint `i`, the Jacobian column is:

```text
J_i = [ z_{i-1} x (o_E - o_{i-1}) ]
      [         z_{i-1}          ]
```

where:

- `o_{i-1}` is the origin of frame `i-1`
- `z_{i-1}` is the joint axis in base coordinates
- `o_E` is the end-effector origin

## Implementation

Frame origins and z-axes come directly from the forward kinematics result:

```text
result.origins
result.z_axes
```

The Jacobian module exposes:

```text
geometric_jacobian(joint_angles)
joint_velocities_from_end_effector(spatial_velocity, joint_angles)
manipulability(joint_angles)
```

## Joint Velocity Recovery

Because the robot has 3 joints, the Jacobian has shape:

```text
J in R^(6 x 3)
```

The minimum-norm solution is computed with the pseudoinverse:

```text
q_dot = pinv(J) * V
```

This gives the best least-squares match to the requested 6D spatial velocity.

## Generated Artifact

The reproducible script is:

```bash
python scripts/phase6_jacobian.py
```

It produces:

```text
outputs/phase6_jacobian.txt
```

The report includes:

- frame origins
- joint axes
- numeric Jacobian
- manipulability
- condition number
- minimum-norm `q_dot`

## Implementation Files

- `src/jacobian.py`
- `scripts/phase6_jacobian.py`
- `tests/test_jacobian.py`
