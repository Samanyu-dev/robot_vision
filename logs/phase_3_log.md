# Phase 3 Log

Date: 2026-04-19

## Objective

Implement the world-to-image projection equation:

```text
P_I = K * [R | t] * P_G
```

## Completed

- Added `src/projection.py`.
- Implemented:

```text
intrinsic_matrix(intrinsics)
world_to_camera_transform(T_GC)
world_to_camera_extrinsic(T_GC)
transform_world_to_camera(P_G, T_GC)
project_camera_point(P_C, K)
project_world_point(P_G, T_GC, K)
camera_matrix(T_GC, K)
```

- Added `CameraIntrinsics` with defaults:

```text
fx = 600 px
fy = 600 px
cx = 320 px
cy = 240 px
width = 640 px
height = 480 px
```

- Added behind-camera and image-bounds checks.
- Added report-ready projection derivation.

## Numerical Example

The script uses the Phase 2 camera pose and:

```text
P_C = [0.05, -0.03, 1.00, 1.00]^T
```

This gives:

```text
u = 350 px
v = 222 px
```

The equivalent world point used in the generated artifact is:

```text
P_G = [1.199568 0.704118 1.514687 1.000000]^T
```

## Verification

Commands run:

```text
.venv/bin/python scripts/phase3_projection.py
.venv/bin/python -m unittest discover -s tests
```

Result:

```text
Ran 19 tests in 0.016s
OK
```

## Planned UI

A small interactive viewer will be added after cube projection is available. It should include joint sliders, a robot view, a camera image view, and an out-of-view indicator.

## Next Phase

Phase 4 will compute image coordinates for a concrete object point/cube vertex using the same projection pipeline.
