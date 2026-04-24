# Commands Reference

This file is the submission runbook for the project. Every command below is written from the project root:

```text
ROBOT_VISION/
```

## 1. Environment Setup

Create the virtual environment:

```bash
python3 -m venv .venv
```

Install dependencies:

```bash
.venv/bin/python -m pip install -r requirements.txt
```

Optional but recommended for plotting commands on systems where `~/.matplotlib` is not writable:

```bash
export MPLCONFIGDIR=/tmp/mpl_robot_vision
```

## 2. Run Individual Phases

Phase 1:

```bash
.venv/bin/python scripts/phase1_forward_kinematics.py
```

Creates:

```text
outputs/phase1_forward_kinematics.txt
```

Phase 2:

```bash
.venv/bin/python scripts/phase2_camera_extrinsics.py
```

Creates:

```text
outputs/phase2_camera_extrinsics.txt
```

Phase 3:

```bash
.venv/bin/python scripts/phase3_projection.py
```

Creates:

```text
outputs/phase3_projection.txt
```

Phase 4:

```bash
.venv/bin/python scripts/phase4_image_coordinates.py
```

Creates:

```text
outputs/phase4_image_coordinates.txt
```

Phase 5:

```bash
.venv/bin/python scripts/phase5_cube_vertices.py
```

Creates:

```text
outputs/phase5_cube_vertices.txt
outputs/phase5_cube_image.png
```

Model note:

```text
Cube center fixed in world frame at P_obj_G = [1.40, 0.60, 1.80]^T m
```

Phase 6:

```bash
.venv/bin/python scripts/phase6_jacobian.py
```

Creates:

```text
outputs/phase6_jacobian.txt
```

Phase 7:

```bash
.venv/bin/python scripts/phase7_trajectory.py
```

Creates:

```text
outputs/phase7_trajectory.txt
outputs/phase7_uv_plot.png
outputs/phase7_uv_vs_time.png
```

Phase 8:

```bash
.venv/bin/python scripts/phase8_simulation_3d.py
```

Creates:

```text
outputs/phase8_simulation_3d.gif
outputs/phase8_snapshot_3d.png
```

Phase 9:

```bash
.venv/bin/python scripts/phase9_camera_view.py
```

Creates:

```text
outputs/phase9_camera_view.gif
outputs/phase9_snapshot_cam.png
```

## 3. Run Everything for Submission

Use this exact sequence:

```bash
export MPLCONFIGDIR=/tmp/mpl_robot_vision
.venv/bin/python scripts/phase1_forward_kinematics.py
.venv/bin/python scripts/phase2_camera_extrinsics.py
.venv/bin/python scripts/phase3_projection.py
.venv/bin/python scripts/phase4_image_coordinates.py
.venv/bin/python scripts/phase5_cube_vertices.py
.venv/bin/python scripts/phase6_jacobian.py
.venv/bin/python scripts/phase7_trajectory.py
.venv/bin/python scripts/phase8_simulation_3d.py
.venv/bin/python scripts/phase9_camera_view.py
```

## 4. Run Validation

Run the full test suite:

```bash
.venv/bin/python -m unittest discover -s tests
```

Expected result:

```text
OK
```

## 5. Inspect Generated Submission Files

List all output files:

```bash
ls -lh outputs
```

View the text outputs quickly:

```bash
sed -n '1,160p' outputs/phase1_forward_kinematics.txt
sed -n '1,160p' outputs/phase2_camera_extrinsics.txt
sed -n '1,160p' outputs/phase3_projection.txt
sed -n '1,160p' outputs/phase4_image_coordinates.txt
sed -n '1,160p' outputs/phase5_cube_vertices.txt
sed -n '1,200p' outputs/phase6_jacobian.txt
sed -n '1,200p' outputs/phase7_trajectory.txt
```

Open the submission report:

```bash
open docs/submission_report.docx
```

## 6. Git Commands

Check repository status:

```bash
git status --short --branch
```

View recent phase commits:

```bash
git log --oneline --decorate --max-count 12
```

Push local commits:

```bash
git push origin main
```

## 7. Submission Checklist

Before submitting, make sure these commands have succeeded:

```bash
.venv/bin/python -m unittest discover -s tests
ls -lh outputs
git status --short --branch
```

The final checks should show:

- tests passing
- all expected output files present
- clean git status or only intentional local media artifacts
