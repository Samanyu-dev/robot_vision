# Robot Vision

Phase-wise implementation of a 3R robot arm with an end-effector mounted camera, camera projection, cube visualization, image-plane simulation, Jacobian-based velocity analysis, trajectory plotting, videos, and report artifacts.

## Execution Plan

1. Phase 0: Understand the system and document the frame pipeline.
2. Phase 1: Define 3R manipulator DH parameters and forward kinematics.
3. Phase 2: Add camera extrinsics on the end-effector.
4. Phase 3: Derive and implement world-to-image projection.
5. Phase 4: Compute image coordinates for a sample cube vertex.
6. Phase 5: Model and project all cube vertices.
7. Phase 6: Compute Jacobian and joint velocities.
8. Phase 7: Track image-plane trajectory.
9. Phase 8: Generate robot/camera/cube simulation video.
10. Phase 9: Generate camera view simulation video.
11. Phase 10: Assemble report material.

## Frame Pipeline

The main mapping is:

```text
Global frame {G} -> Robot base {B} -> End-effector {E} -> Camera {C} -> Image {I}
```

With the base at the global origin:

```text
T_GC = T_BE * T_EC
P_C = inv(T_GC) * P_G
P_I = K * [R | t] * P_G
```

The detailed Phase 0 mental model is in [docs/phase_0_system_model.md](docs/phase_0_system_model.md).

## Project Structure

```text
robot_vision/
├── README.md
├── requirements.txt
├── docs/
├── logs/
├── outputs/
├── src/
└── tests/
```

## Dependencies

Core tools:

- Python 3.9+
- NumPy
- SciPy
- Matplotlib
- OpenCV

Install later with:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

See [docs/commands_reference.md](docs/commands_reference.md) for the commands to run for each phase and what each output represents.

## GitHub Status

The local repository is initialized during Phase 0. Remote GitHub creation requires either:

- GitHub CLI installed and authenticated with `gh auth login`, or
- an empty GitHub repository created manually named `robot_vision`, followed by adding its remote URL locally.
