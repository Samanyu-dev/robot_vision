# Phase 7: Image-Plane Trajectory

## Objective

Drive the 3R arm through a time-varying joint trajectory and track one cube vertex in image coordinates over time.

## Joint Motion

The joint inputs are:

```text
theta_1(t) = 30 deg + 20 deg sin(t)
theta_2(t) = 45 deg + 15 deg sin(2t)
theta_3(t) = -20 deg + 10 deg cos(t)
```

The simulation uses:

```text
t in [0, 2*pi]
N = 200 samples
```

## Tracking Setup

At each sample:

1. compute `T_GC`
2. keep the cube center fixed at `P_obj_G = [1.40, 0.60, 1.80]^T m`
3. select the vertex `(+L/2, +L/2, +L/2)`
4. project to `(u, v)`

This creates a camera-relative motion trace for a single cube corner.

## Generated Artifacts

The reproducible script is:

```bash
python scripts/phase7_trajectory.py
```

It produces:

```text
outputs/phase7_trajectory.txt
outputs/phase7_uv_plot.png
outputs/phase7_uv_vs_time.png
```

The outputs show:

- sampled text rows of `(u, v)` values
- the trajectory path in image coordinates
- `u(t)` and `v(t)` plots across time

## Implementation Files

- `scripts/phase7_trajectory.py`
