# Phase 8: 3D Robot Simulation

## Objective

Animate the robot, the wrist-mounted camera, and the observed cube in a shared 3D world view.

## Scene Content

Each animation frame renders:

- the global frame
- robot links and joints
- local frame axes
- the camera position and optical direction
- the cube wireframe
- an end-effector trail

The same time-varying joint trajectory from Phase 7 is reused.

## Generated Artifacts

The reproducible script is:

```bash
python scripts/phase8_simulation_3d.py
```

It produces:

```text
outputs/phase8_simulation_3d.gif
outputs/phase8_snapshot_3d.png
```

The GIF gives an animated 3D overview, while the PNG preserves a clean reference frame at `t = 0`.

## Implementation Files

- `scripts/phase8_simulation_3d.py`
