# Phase 4 Log

Date: 2026-04-19

## Objective

Compute image coordinates for one cube vertex using the full transform chain:

```text
T_BE -> T_GC -> P_C -> (u, v)
```

## Completed

- Added `src/cube.py`.
- Implemented:

```text
cube_vertices_local(side_length)
cube_vertices_world(center, side_length)
cube_vertex_world(center, side_length, signs)
```

- Added `scripts/phase4_image_coordinates.py`.
- Added `tests/test_cube.py`.
- Added a command reference document at `docs/commands_reference.md`.

## Numerical Example

The script uses:

```text
theta = [30 deg, 45 deg, -20 deg]
cube side length = 0.20 m
selected vertex signs = (1, 1, 1)
```

The cube center is selected 1.20 m along the camera optical axis for the sample pose, then expressed in world coordinates.

The selected vertex projects to:

```text
(u, v) = (336.061926, 228.642503)
```

The vertex is:

```text
in front of camera = True
inside 640 x 480 image bounds = True
```

Detailed generated values:

```text
P_center_G = [1.328671 0.720921 1.677321]^T m
P_vertex_G = [1.428671 0.820921 1.777321]^T m
P_vertex_C = [0.036603 -0.025882 1.367303 1.000000]^T m
```

## Verification

Commands run:

```text
.venv/bin/python scripts/phase4_image_coordinates.py
.venv/bin/python -m unittest discover -s tests
```

Result:

```text
Ran 24 tests in 0.012s
OK
```

## Next Phase

Phase 5 will define and project all 8 cube vertices and prepare the cube edge list for image-plane drawing.
