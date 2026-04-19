"""Phase 9 - Animated camera-view dashboard.

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
from matplotlib.gridspec import GridSpec
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
TRACKED_VERTEX_INDEX = 6


def joint_angles_at(t_value: float) -> np.ndarray:
    """Return the robot trajectory at time t."""

    return np.deg2rad(
        [
            30.0 + 20.0 * np.sin(t_value),
            45.0 + 15.0 * np.sin(2.0 * t_value),
            -20.0 + 10.0 * np.cos(t_value),
        ]
    )


def build_frame_data() -> dict[str, np.ndarray]:
    """Precompute projection data used by the dashboard plots."""

    pixels = np.full((N_FRAMES, 8, 2), np.nan, dtype=float)
    visible = np.zeros((N_FRAMES, 8), dtype=bool)
    tracked_depth = np.full(N_FRAMES, np.nan, dtype=float)

    for frame_index, t_value in enumerate(T_VEC):
        angles = joint_angles_at(t_value)
        t_g_c = camera_pose_in_global(angles, mount=MOUNT)
        cube_center = (t_g_c @ np.array([0.0, 0.0, 1.20, 1.0], dtype=float))[:3]
        vertices = cube_vertices_world(cube_center, CUBE_SIDE)

        for vertex_index, vertex in enumerate(vertices):
            result = project_world_point(vertex, t_g_c, INTRINSICS)
            if result.in_front:
                pixels[frame_index, vertex_index] = result.pixel
            visible[frame_index, vertex_index] = result.in_front and result.in_bounds

            if vertex_index == TRACKED_VERTEX_INDEX and result.in_front:
                tracked_depth[frame_index] = result.camera_point[2]

    visible_counts = visible.sum(axis=1)
    tracked_u = pixels[:, TRACKED_VERTEX_INDEX, 0]
    tracked_v = pixels[:, TRACKED_VERTEX_INDEX, 1]

    return {
        "pixels": pixels,
        "visible": visible,
        "visible_counts": visible_counts,
        "tracked_u": tracked_u,
        "tracked_v": tracked_v,
        "tracked_depth": tracked_depth,
    }


FRAME_DATA = build_frame_data()


def style_plot_axis(axis: plt.Axes, title: str) -> None:
    """Apply the shared dark theme to a 2D axis."""

    axis.set_facecolor("#10161f")
    axis.tick_params(colors="white", labelsize=8)
    for spine in axis.spines.values():
        spine.set_edgecolor("#4b5665")
    axis.grid(True, color="#2f3b4c", linewidth=0.6, alpha=0.7)
    axis.set_title(title, color="white", fontsize=10)


def draw_camera_panel(axis: plt.Axes, frame_index: int) -> None:
    """Render the camera image with projected cube and trajectory trail."""

    pixels = FRAME_DATA["pixels"][frame_index]
    visible = FRAME_DATA["visible"][frame_index]
    tracked_u = FRAME_DATA["tracked_u"][: frame_index + 1]
    tracked_v = FRAME_DATA["tracked_v"][: frame_index + 1]
    valid_trail = ~np.isnan(tracked_u) & ~np.isnan(tracked_v)

    axis.set_facecolor("#111111")
    axis.set_xlim(0, W)
    axis.set_ylim(H, 0)
    axis.set_aspect("equal")
    axis.tick_params(colors="white", labelsize=8)
    for spine in axis.spines.values():
        spine.set_edgecolor("#555555")
    axis.set_xlabel("u (px)", color="white")
    axis.set_ylabel("v (px)", color="white")
    axis.set_title(
        f"Phase 9 - Camera View Dashboard  [t = {T_VEC[frame_index]:.2f} s]",
        color="white",
        fontsize=12,
    )
    axis.add_patch(
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
    axis.plot(INTRINSICS.cx, INTRINSICS.cy, "r+", markersize=16, markeredgewidth=2.5, zorder=10)

    for index0, index1 in CUBE_EDGES:
        if not np.isnan(pixels[index0]).any() and not np.isnan(pixels[index1]).any():
            axis.plot(
                [pixels[index0, 0], pixels[index1, 0]],
                [pixels[index0, 1], pixels[index1, 1]],
                color="deepskyblue",
                linewidth=1.8,
            )

    if valid_trail.any():
        axis.plot(
            tracked_u[valid_trail],
            tracked_v[valid_trail],
            color="#ffe082",
            linewidth=1.2,
            linestyle="--",
            alpha=0.8,
        )

    for index, (pixel, is_visible) in enumerate(zip(pixels, visible)):
        if not np.isnan(pixel).any():
            color = "lime" if is_visible else "orange"
            marker_size = 8 if index == TRACKED_VERTEX_INDEX else 6.5
            axis.plot(pixel[0], pixel[1], "o", color=color, markersize=marker_size, zorder=5)
            axis.text(pixel[0] + 5, pixel[1] - 5, str(index), color=color, fontsize=8)

    if not all(visible):
        axis.text(
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

    axis.text(
        12,
        38,
        (
            f"Visible vertices: {FRAME_DATA['visible_counts'][frame_index]}/8\n"
            f"Tracked vertex: {TRACKED_VERTEX_INDEX} (+,+,+)\n"
            f"Depth z_C: {FRAME_DATA['tracked_depth'][frame_index]:.3f} m"
        ),
        color="white",
        fontsize=8,
        ha="left",
        va="top",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#121821", edgecolor="#334155", alpha=0.85),
    )


def draw_uv_plot(axis: plt.Axes, frame_index: int) -> None:
    """Draw u(t) and v(t) with current-frame markers."""

    style_plot_axis(axis, "Tracked Vertex Pixel History")
    tracked_u = FRAME_DATA["tracked_u"]
    tracked_v = FRAME_DATA["tracked_v"]

    axis.plot(T_VEC, tracked_u, color="#40c4ff", linewidth=1.8, label="u(t)")
    axis.plot(T_VEC, tracked_v, color="#ff5ad1", linewidth=1.8, label="v(t)")
    axis.plot(T_VEC[frame_index], tracked_u[frame_index], "o", color="#40c4ff", markersize=5)
    axis.plot(T_VEC[frame_index], tracked_v[frame_index], "o", color="#ff5ad1", markersize=5)
    axis.axvline(T_VEC[frame_index], color="white", linewidth=1.0, linestyle="--", alpha=0.8)
    axis.axhline(INTRINSICS.cx, color="#40c4ff", linewidth=0.9, linestyle=":", alpha=0.55)
    axis.axhline(INTRINSICS.cy, color="#ff5ad1", linewidth=0.9, linestyle=":", alpha=0.55)
    axis.set_ylabel("Pixel value", color="white")
    axis.legend(facecolor="#1b2532", edgecolor="#405063", labelcolor="white", fontsize=8)


def draw_visibility_plot(axis: plt.Axes, frame_index: int) -> None:
    """Draw visible-vertex count through time."""

    style_plot_axis(axis, "Visible Vertices")
    visible_counts = FRAME_DATA["visible_counts"]

    axis.plot(T_VEC, visible_counts, color="#69f0ae", linewidth=1.8, label="Visible vertices")
    axis.plot(T_VEC[frame_index], visible_counts[frame_index], "o", color="#69f0ae", markersize=5)
    axis.axvline(T_VEC[frame_index], color="white", linewidth=1.0, linestyle="--", alpha=0.8)
    axis.set_ylabel("Visible count", color="white")
    axis.set_ylim(-0.2, 8.5)
    axis.legend(facecolor="#1b2532", edgecolor="#405063", labelcolor="white", fontsize=8)


def draw_depth_plot(axis: plt.Axes, frame_index: int) -> None:
    """Draw tracked vertex depth in the camera frame."""

    style_plot_axis(axis, "Tracked Vertex Depth")
    tracked_depth = FRAME_DATA["tracked_depth"]

    axis.plot(T_VEC, tracked_depth, color="#ffe082", linewidth=1.8, linestyle="--", label="Depth z_C")
    axis.plot(T_VEC[frame_index], tracked_depth[frame_index], "o", color="#ffe082", markersize=5)
    axis.axvline(T_VEC[frame_index], color="white", linewidth=1.0, linestyle="--", alpha=0.8)
    axis.set_xlabel("t [s]", color="white")
    axis.set_ylabel("Depth [m]", color="white")
    axis.legend(facecolor="#1b2532", edgecolor="#405063", labelcolor="white", fontsize=8)


def render_dashboard(frame_index: int) -> plt.Figure:
    """Create the camera-view dashboard for a frame."""

    fig = plt.figure(figsize=(13.5, 7.8), facecolor="#0b1017")
    grid = GridSpec(
        3,
        2,
        figure=fig,
        width_ratios=(1.75, 1.0),
        height_ratios=(1.0, 0.82, 0.82),
        hspace=0.24,
        wspace=0.18,
    )

    ax_camera = fig.add_subplot(grid[:, 0])
    ax_uv = fig.add_subplot(grid[0, 1])
    ax_visibility = fig.add_subplot(grid[1, 1])
    ax_depth = fig.add_subplot(grid[2, 1])

    draw_camera_panel(ax_camera, frame_index)
    draw_uv_plot(ax_uv, frame_index)
    draw_visibility_plot(ax_visibility, frame_index)
    draw_depth_plot(ax_depth, frame_index)

    fig.subplots_adjust(left=0.05, right=0.98, top=0.94, bottom=0.08)
    return fig


def main() -> None:
    output_dir = PROJECT_ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)

    dashboard_fig = render_dashboard(0)
    axes = dashboard_fig.axes
    camera_ax = axes[0]
    uv_ax = axes[1]
    visibility_ax = axes[2]
    depth_ax = axes[3]

    def update(frame_index: int) -> None:
        camera_ax.cla()
        uv_ax.cla()
        visibility_ax.cla()
        depth_ax.cla()
        draw_camera_panel(camera_ax, frame_index)
        draw_uv_plot(uv_ax, frame_index)
        draw_visibility_plot(visibility_ax, frame_index)
        draw_depth_plot(depth_ax, frame_index)

    animation = FuncAnimation(
        dashboard_fig,
        update,
        frames=N_FRAMES,
        interval=80,
        blit=False,
        repeat=False,
    )
    animation.save(
        str(output_dir / "phase9_camera_view.gif"),
        writer=PillowWriter(fps=12),
    )
    plt.close(dashboard_fig)
    print("Saved: outputs/phase9_camera_view.gif")

    snapshot_fig = render_dashboard(0)
    snapshot_fig.savefig(
        str(output_dir / "phase9_snapshot_cam.png"),
        dpi=150,
        facecolor=snapshot_fig.get_facecolor(),
    )
    plt.close(snapshot_fig)
    print("Saved: outputs/phase9_snapshot_cam.png")


if __name__ == "__main__":
    main()
