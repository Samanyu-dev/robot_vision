# Phase 8: 3D Robot Simulation

## Objective

Animate the robot, the wrist-mounted camera, and the observed cube in a shared 3D world view, then package the result as a submission-ready dashboard.

The cube is fixed in the global frame at:

```text
P_obj_G = [1.40, 0.60, 1.80]^T m
```

## Scene Content

Each animation frame renders:

- the global frame
- robot links and joints
- the wrist frame at the end-effector
- the camera position and optical direction
- the camera frame at the camera origin
- a camera frustum estimate
- the cube wireframe
- translucent cube faces
- an end-effector trail
- joint-angle plots over time
- workspace metric plots over time

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

The GIF gives an animated dashboard with:

- a large 3D scene view
- current joint-angle markers
- end-effector position traces
- camera-to-cube distance trace

The PNG preserves the same dashboard layout at `t = 0`, which is useful for submission screenshots.

## Implementation Files

- `scripts/phase8_simulation_3d.py`
