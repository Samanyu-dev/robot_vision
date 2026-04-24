# Phase 5 Log

Date: 2026-04-19

## Objective

Project all 8 cube vertices, add cube edge connectivity, and render the wireframe in the camera image.

## Completed

- Updated `src/cube.py` with `CUBE_EDGES`.
- Added `scripts/phase5_cube_vertices.py`.
- Added `docs/phase_5_cube_vertices.md`.
- Added `logs/phase_5_log.md`.
- Fixed the cube center in the global frame at `P_obj_G = [1.40, 0.60, 1.80]^T m`.

## Verification

Commands run:

```text
.venv/bin/python scripts/phase5_cube_vertices.py
```

Key result:

```text
All vertices in view: True
```

Artifacts generated:

```text
outputs/phase5_cube_vertices.txt
outputs/phase5_cube_image.png
```
