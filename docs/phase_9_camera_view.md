# Phase 9: Camera View Simulation

## Objective

Animate the projected cube directly in the image plane and present it as a dashboard-style camera feed for submission.

The cube itself remains fixed in the global frame at:

```text
P_obj_G = [1.40, 0.60, 1.80]^T m
```

## View Content

Each frame renders:

- the 640 x 480 image border
- the principal point
- projected cube edges
- vertex markers and labels
- a trail for vertex 6 `(+,+,+)`
- an `"OBJECT OUT OF VIEW"` warning banner when needed
- `u(t)` and `v(t)` plots for the tracked vertex
- visible-vertex count over time
- tracked depth `z_C` over time

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

The GIF is an animated camera dashboard. The PNG is a matching reference dashboard snapshot at `t = 0`.

## Implementation Files

- `scripts/phase9_camera_view.py`
