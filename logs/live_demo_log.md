# Live Demo Log

Date: 2026-04-23

## Objective

Prepare the repository for a public live demo link, similar to a website URL for a web project.

## Decision

Use Streamlit Community Cloud as the primary deployment target.

Reasons:

- runs Python directly from GitHub
- supports interactive sliders
- supports Matplotlib figures
- provides a shareable `streamlit.app` URL
- fits the current robot kinematics and camera projection code without a rewrite

## Completed

- Added root-level Streamlit entry point:

```text
app.py
```

- Added deployment guide:

```text
docs/live_demo.md
```

- Updated:

```text
README.md
docs/commands_reference.md
requirements.txt
```

- Added `streamlit` to dependencies.

## App Features

The app includes:

- joint sliders for `theta_1`, `theta_2`, and `theta_3`
- cube side-length and center controls
- focal-length and camera-tilt controls
- 3D robot/camera/cube plot
- 640 x 480 image-plane projection plot
- visible-vertex count
- in-view/out-of-view status

## Verification

Commands run:

```text
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests
env MPLBACKEND=Agg MPLCONFIGDIR=/tmp/mpl_robot_vision .venv/bin/python -c 'import sys; sys.path.insert(0, "."); import app; import numpy as np; from camera import CameraMount, camera_pose_in_global; from cube import DEFAULT_CUBE_CENTER_G, DEFAULT_CUBE_SIDE_LENGTH, cube_vertices_world; angles=np.deg2rad([30,45,-20]); t=camera_pose_in_global(angles, mount=CameraMount()); verts=cube_vertices_world(DEFAULT_CUBE_CENTER_G, DEFAULT_CUBE_SIDE_LENGTH); fig=app.build_robot_plot(angles, verts, t); fig.savefig("/tmp/mpl_robot_vision/app_check.png"); print("app import and figure build OK")'
```

Results:

```text
Ran 29 tests in 0.013s
OK
app import and figure build OK
```

## Deployment Step Remaining

The user needs to create the public deployment from Streamlit Community Cloud:

```text
Repository: Samanyu-dev/robot_vision
Branch: main
App file: app.py
```

After deployment, copy the generated `streamlit.app` URL into the README live-demo section.

