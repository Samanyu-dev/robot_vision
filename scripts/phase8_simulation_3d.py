"""Phase 8 - Animated 3D robot simulation.

Outputs
-------
outputs/phase8_simulation_3d.gif
outputs/phase8_snapshot_3d.png
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

matplotlib.use("Agg")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from camera import CameraMount, camera_pose_in_global  # noqa: E402
from cube import CUBE_EDGES, cube_vertices_world  # noqa: E402
from kinematics import forward_kinematics  # noqa: E402

N_FRAMES = 80
T_TOTAL = 2.0 * np.pi
T_VEC = np.linspace(0.0, T_TOTAL, N_FRAMES)
MOUNT = CameraMount(translation_e=(0.08, 0.0, 0.04), tilt_rad=np.deg2rad(-20.0))
CUBE_SIDE = 0.20
AXIS_LEN = 0.12


def joint_angles_at(t_value: float) -> np.ndarray:
    """Return the robot trajectory at time t."""

    return np.deg2rad(
        [
            30.0 + 20.0 * np.sin(t_value),
            45.0 + 15.0 * np.sin(2.0 * t_value),
            -20.0 + 10.0 * np.cos(t_value),
        ]
    )


FRAMES_DATA = [
    (
        joint_angles_at(t_value),
        (camera_pose_in_global(joint_angles_at(t_value), mount=MOUNT) @ np.array([0.0, 0.0, 1.20, 1.0]))[:3],
    )
    for t_value in T_VEC
]


def draw_frame_axes(ax: Axes3D, transform: np.ndarray, scale: float = AXIS_LEN) -> None:
    """Draw local xyz axes for a homogeneous transform."""

    origin = transform[:3, 3]
    for column, color in zip(range(3), ("red", "lime", "blue")):
        ax.quiver(
            *origin,
            *(transform[:3, column] * scale),
            color=color,
            linewidth=1.2,
            arrow_length_ratio=0.3,
        )


def setup_ax(ax: Axes3D, t_label: str = "") -> None:
    """Configure the shared 3D axes styling."""

    ax.set_facecolor("#111111")
    ax.set_xlim(-0.3, 1.8)
    ax.set_ylim(-0.8, 0.8)
    ax.set_zlim(0.0, 1.9)
    ax.set_xlabel("X [m]", color="white")
    ax.set_ylabel("Y [m]", color="white")
    ax.set_zlabel("Z [m]", color="white")
    ax.tick_params(colors="white")
    ax.set_title(f"Phase 8 - 3D Robot Simulation  {t_label}", color="white", fontsize=11)
    for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
        pane.fill = False
        pane.set_edgecolor("#333333")


def draw_scene(
    ax: Axes3D,
    angles: np.ndarray,
    cube_center: np.ndarray,
    trail_points: list[np.ndarray],
) -> None:
    """Draw the robot, camera, cube, and trail for one frame."""

    result = forward_kinematics(angles)
    t_g_c = camera_pose_in_global(angles, mount=MOUNT)
    origins = result.origins

    for direction, color in zip(np.eye(3), ("red", "lime", "blue")):
        ax.quiver(0.0, 0.0, 0.0, *(direction * AXIS_LEN * 2.0), color=color, linewidth=2.0)

    for index in range(len(origins) - 1):
        ax.plot(
            [origins[index, 0], origins[index + 1, 0]],
            [origins[index, 1], origins[index + 1, 1]],
            [origins[index, 2], origins[index + 1, 2]],
            color="#4fc3f7",
            linewidth=4,
        )

    for origin in origins:
        ax.scatter(*origin, color="white", s=40, depthshade=False)

    for transform in result.transforms:
        draw_frame_axes(ax, transform)

    camera_origin = t_g_c[:3, 3]
    ax.scatter(*camera_origin, color="magenta", s=80, marker="s", depthshade=False)
    ax.quiver(
        *camera_origin,
        *(t_g_c[:3, 2] * 0.25),
        color="magenta",
        linewidth=1.5,
        arrow_length_ratio=0.3,
    )

    vertices = cube_vertices_world(cube_center, CUBE_SIDE)
    for index0, index1 in CUBE_EDGES:
        ax.plot(
            [vertices[index0, 0], vertices[index1, 0]],
            [vertices[index0, 1], vertices[index1, 1]],
            [vertices[index0, 2], vertices[index1, 2]],
            color="red",
            linewidth=1.5,
        )

    if len(trail_points) >= 2:
        points = np.array(trail_points)
        ax.plot(
            points[:, 0],
            points[:, 1],
            points[:, 2],
            color="black",
            linewidth=1.2,
            linestyle="--",
            alpha=0.8,
        )


def main() -> None:
    output_dir = PROJECT_ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)

    fig = plt.figure(figsize=(10, 8), facecolor="#111111")
    ax = fig.add_subplot(111, projection="3d")
    trail: list[np.ndarray] = []

    def update(frame_index: int) -> None:
        ax.cla()
        setup_ax(ax, f"[t = {T_VEC[frame_index]:.2f} s]")
        angles, cube_center = FRAMES_DATA[frame_index]
        draw_scene(ax, angles, cube_center, trail)
        trail.append(forward_kinematics(angles).origins[-1].copy())

    animation = FuncAnimation(fig, update, frames=N_FRAMES, interval=80, repeat=False)
    animation.save(
        str(output_dir / "phase8_simulation_3d.gif"),
        writer=PillowWriter(fps=12),
    )
    plt.close(fig)
    print("Saved: outputs/phase8_simulation_3d.gif")

    fig_snapshot = plt.figure(figsize=(10, 8), facecolor="#111111")
    ax_snapshot = fig_snapshot.add_subplot(111, projection="3d")
    setup_ax(ax_snapshot, "[t = 0.00 s]")
    angles0, center0 = FRAMES_DATA[0]
    draw_scene(ax_snapshot, angles0, center0, [])
    fig_snapshot.savefig(
        str(output_dir / "phase8_snapshot_3d.png"),
        dpi=150,
        facecolor=fig_snapshot.get_facecolor(),
    )
    plt.close(fig_snapshot)
    print("Saved: outputs/phase8_snapshot_3d.png")


if __name__ == "__main__":
    main()
