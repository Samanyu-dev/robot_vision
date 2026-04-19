# Commands Reference

This file lists the main commands for the project, when to use them, and what their outputs mean.

## Environment Setup

Create a virtual environment:

```bash
python3 -m venv .venv
```

Use when starting on a fresh machine or after deleting `.venv`.

Output meaning:

- no output usually means the environment was created successfully
- `.venv/` appears in the project folder

Install dependencies:

```bash
.venv/bin/python -m pip install -r requirements.txt
```

Use after creating `.venv` or after changing `requirements.txt`.

Output meaning:

- package download/install lines show dependency installation progress
- `Successfully installed ...` means dependencies are ready
- network errors mean the machine cannot reach PyPI or needs network approval

## Validation

Run all tests:

```bash
.venv/bin/python -m unittest discover -s tests
```

Use after every phase or before pushing.

Output meaning:

- `OK` means all tests passed
- `FAILED` means at least one behavior check failed and should be fixed before pushing
- the number after `Ran` tells how many unit tests were executed

## Phase Scripts

Run Phase 1 forward kinematics:

```bash
.venv/bin/python scripts/phase1_forward_kinematics.py
```

Use when checking DH parameters and end-effector pose.

Output meaning:

- `T_B1`, `T_B2`, and `T_B3` are the base-to-link transforms
- `T_BE` is the final end-effector pose
- `End-effector position [m]` is the wrist/end-effector origin in base coordinates
- result file: `outputs/phase1_forward_kinematics.txt`

Run Phase 2 camera extrinsics:

```bash
.venv/bin/python scripts/phase2_camera_extrinsics.py
```

Use when checking the wrist-mounted camera transform.

Output meaning:

- `T_EC` is the camera pose relative to the end-effector
- `T_GC` is the camera pose relative to the global/base frame
- `Camera origin` is the camera center in world coordinates
- `Camera optical axis +Z_C` shows where the camera is looking in world coordinates
- result file: `outputs/phase2_camera_extrinsics.txt`

Run Phase 3 projection:

```bash
.venv/bin/python scripts/phase3_projection.py
```

Use when checking the world-to-image projection derivation.

Output meaning:

- `K` is the intrinsic matrix
- `T_CG = inv(T_GC)` transforms world points into the camera frame
- `[R | t]` is the world-to-camera extrinsic matrix
- `K [R | t]` is the camera projection matrix
- `Pixel projection [u, v]` is the final image coordinate
- result file: `outputs/phase3_projection.txt`

Run Phase 4 one-vertex image coordinate calculation:

```bash
.venv/bin/python scripts/phase4_image_coordinates.py
```

Use when checking a concrete cube vertex projection.

Output meaning:

- `Cube setup` defines cube side length, center, and selected vertex
- `Selected cube vertex in world frame P_G` is the object point before camera transform
- `Selected cube vertex in camera frame P_C` is the same point after `inv(T_GC)`
- `Pixel coordinate [u, v]` is the final image coordinate
- `Inside 640 x 480 image bounds` tells whether the vertex is visible in the image
- result file: `outputs/phase4_image_coordinates.txt`

## Git Commands

Check current git state:

```bash
git status --short --branch
```

Use before and after each phase.

Output meaning:

- `## main...origin/main` with no changed files means local and remote are clean and synced
- lines beginning with `M` are modified files
- lines beginning with `??` are untracked files

View recent commits:

```bash
git log --oneline --decorate --max-count 8
```

Use to confirm phase checkpoints.

Output meaning:

- the first line is the current commit
- `HEAD -> main, origin/main` means the current local branch and GitHub remote point to the same commit

Push current branch:

```bash
git push origin main
```

Use after committing a phase.

Output meaning:

- `main -> main` means the commit was pushed to GitHub
- `Everything up-to-date` means there is nothing new to push
- authentication or repository errors mean GitHub credentials or remote setup need attention

