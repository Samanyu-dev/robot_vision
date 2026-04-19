"""Phase 9 - Animated 640 x 480 camera-view simulation.

Outputs
-------
outputs/phase9_camera_view.gif
outputs/phase9_snapshot_cam.png
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Rectangle

matplotlib.use("Agg")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from camera import CameraMount, camera_pose_in_global  # noqa: E402
from cube import CUBE_EDGES, cube_vertices_world  # noqa: E402
from projection import CameraIntrinsics, project_world_point  # noqa: E402

N_FRAMES = 80
T_TOTAL = 2.0 * np.pi
T_VEC = np.linspace(0.0, T_TOTAL, N_FRAMES)
MOUNT = CameraMount(translation_e=(0.08, 0.0, 0.04), tilt_rad=np.deg2rad(-20.0))
INTRINSICS = CameraIntrinsics(fx=600.0, fy=600.0, cx=320.0, cy=240.0)
CUBE_SIDE = 0.20
W, H = INTRINSICS.width, INTRINSICS.height


def joint_angles_at(t_value: float) -> np.ndarray:
    """Return the robot trajectory at time t."""

    return np.deg2rad(
        [
            30.0 + 20.0 * np.sin(t_value),
            45.0 + 15.0 * np.sin(2.0 * t_value),
            -20.0 + 10.0 * np.cos(t_value),
        ]
    )


def get_frame_pixels(t_value: float) -> tuple[np.ndarray, list[bool]]:
    """Project all cube vertices for a given time sample."""

    angles = joint_angles_at(t_value)
    t_g_c = camera_pose_in_global(angles, mount=MOUNT)
    cube_center = (t_g_c @ np.array([0.0, 0.0, 1.20, 1.0], dtype=float))[:3]
    vertices = cube_vertices_world(cube_center, CUBE_SIDE)
    pixels = np.full((8, 2), np.nan, dtype=float)
    visible: list[bool] = []

    for index, vertex in enumerate(vertices):
        result = project_world_point(vertex, t_g_c, INTRINSICS)
        if result.in_front:
            pixels[index] = result.pixel
        visible.append(result.in_front and result.in_bounds)

    return pixels, visible


def main() -> None:
    output_dir = PROJECT_ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor("#111111")
    ax.set_facecolor("#111111")
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_aspect("equal")
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#555555")
    ax.set_xlabel("u (px)", color="white")
    ax.set_ylabel("v (px)", color="white")

    ax.add_patch(
        Rectangle(
            (0, 0),
            W,
            H,
            edgecolor="white",
            facecolor="none",
            linewidth=1.2,
            linestyle="--",
        )
    )
    ax.plot(INTRINSICS.cx, INTRINSICS.cy, "r+", markersize=16, markeredgewidth=2.5, zorder=10)

    edge_lines = [
        ax.plot([], [], color="deepskyblue", linewidth=1.8)[0] for _ in CUBE_EDGES
    ]
    vertex_dots = [
        ax.plot([], [], "o", color="lime", markersize=7, zorder=5)[0] for _ in range(8)
    ]
    vertex_labels = [
        ax.text(0, 0, str(index), color="lime", fontsize=7, visible=False)
        for index in range(8)
    ]
    trail_line = ax.plot([], [], color="yellow", linewidth=1.0, linestyle="--", alpha=0.6)[0]
    out_text = ax.text(
        W / 2.0,
        H / 2.0,
        "",
        color="red",
        fontsize=14,
        fontweight="bold",
        ha="center",
        va="center",
        bbox=dict(boxstyle="round,pad=0.5", fc="black", alpha=0.7),
    )
    time_text = ax.text(10, 20, "", color="white", fontsize=9)
    ax.set_title("Phase 9 - Camera View Simulation", color="white", fontsize=12)

    trail_u: list[float] = []
    trail_v: list[float] = []

    def update(frame_index: int):
        pixels, visible = get_frame_pixels(T_VEC[frame_index])
        time_text.set_text(f"t = {T_VEC[frame_index]:.2f} s")

        if not np.isnan(pixels[6]).any():
            trail_u.append(float(pixels[6, 0]))
            trail_v.append(float(pixels[6, 1]))
        trail_line.set_data(trail_u, trail_v)

        for line, (index0, index1) in zip(edge_lines, CUBE_EDGES):
            if not np.isnan(pixels[index0]).any() and not np.isnan(pixels[index1]).any():
                line.set_data(
                    [pixels[index0, 0], pixels[index1, 0]],
                    [pixels[index0, 1], pixels[index1, 1]],
                )
            else:
                line.set_data([], [])

        for index, (dot, label) in enumerate(zip(vertex_dots, vertex_labels)):
            if not np.isnan(pixels[index]).any():
                dot.set_data([pixels[index, 0]], [pixels[index, 1]])
                color = "lime" if visible[index] else "orange"
                dot.set_color(color)
                label.set_color(color)
                label.set_position((pixels[index, 0] + 5, pixels[index, 1] - 5))
                label.set_visible(True)
            else:
                dot.set_data([], [])
                label.set_visible(False)

        out_text.set_text("SOME VERTICES OUT OF VIEW" if not all(visible) else "")
        return edge_lines + vertex_dots + vertex_labels + [trail_line, out_text, time_text]

    animation = FuncAnimation(fig, update, frames=N_FRAMES, interval=80, blit=False, repeat=False)
    animation.save(
        str(output_dir / "phase9_camera_view.gif"),
        writer=PillowWriter(fps=12),
    )
    plt.close(fig)
    print("Saved: outputs/phase9_camera_view.gif")

    fig_snapshot, ax_snapshot = plt.subplots(figsize=(8, 6))
    fig_snapshot.patch.set_facecolor("#111111")
    ax_snapshot.set_facecolor("#111111")
    ax_snapshot.set_xlim(0, W)
    ax_snapshot.set_ylim(H, 0)
    ax_snapshot.set_aspect("equal")
    ax_snapshot.tick_params(colors="white")
    for spine in ax_snapshot.spines.values():
        spine.set_edgecolor("#555555")
    ax_snapshot.add_patch(
        Rectangle(
            (0, 0),
            W,
            H,
            edgecolor="white",
            facecolor="none",
            linewidth=1.2,
            linestyle="--",
        )
    )
    ax_snapshot.plot(INTRINSICS.cx, INTRINSICS.cy, "r+", markersize=16, markeredgewidth=2.5, zorder=10)

    pixels, visible = get_frame_pixels(0.0)
    for index0, index1 in CUBE_EDGES:
        if not np.isnan(pixels[index0]).any() and not np.isnan(pixels[index1]).any():
            ax_snapshot.plot(
                [pixels[index0, 0], pixels[index1, 0]],
                [pixels[index0, 1], pixels[index1, 1]],
                color="deepskyblue",
                linewidth=1.8,
            )
    for index, (pixel, is_visible) in enumerate(zip(pixels, visible)):
        if not np.isnan(pixel).any():
            color = "lime" if is_visible else "orange"
            ax_snapshot.plot(pixel[0], pixel[1], "o", color=color, markersize=8, zorder=5)
            ax_snapshot.text(pixel[0] + 5, pixel[1] - 5, str(index), color=color, fontsize=8)
    if not all(visible):
        ax_snapshot.text(
            W / 2.0,
            H / 2.0,
            "SOME VERTICES OUT OF VIEW",
            color="red",
            fontsize=14,
            fontweight="bold",
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.5", fc="black", alpha=0.7),
        )
    ax_snapshot.set_title("Phase 9 - Camera View Snapshot (t = 0)", color="white")
    ax_snapshot.set_xlabel("u (px)", color="white")
    ax_snapshot.set_ylabel("v (px)", color="white")
    fig_snapshot.tight_layout()
    fig_snapshot.savefig(
        str(output_dir / "phase9_snapshot_cam.png"),
        dpi=150,
        facecolor=fig_snapshot.get_facecolor(),
    )
    plt.close(fig_snapshot)
    print("Saved: outputs/phase9_snapshot_cam.png")


if __name__ == "__main__":
    main()
