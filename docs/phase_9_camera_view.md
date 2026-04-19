# Phase 9: Camera View Simulation

## Objective

Animate the projected cube directly in the image plane to simulate the live output of the wrist camera.

## View Content

Each frame renders:

- the 640 x 480 image border
- the principal point
- projected cube edges
- vertex markers and labels
- a trail for vertex 6 `(+,+,+)`
- an out-of-view warning banner when needed

This phase reuses the same motion profile as Phase 7 and the same cube edge topology from Phase 5.

## Generated Artifacts

The reproducible script is:

```bash
python scripts/phase9_camera_view.py
```

It produces:

```text
outputs/phase9_camera_view.gif
outputs/phase9_snapshot_cam.png
```

The GIF is the animated camera feed. The PNG is a single reference snapshot at `t = 0`.

## Implementation Files

- `scripts/phase9_camera_view.py`
