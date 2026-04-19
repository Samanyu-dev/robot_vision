"""Phase 7 - Joint trajectory and image-plane tracking.

Joint motion:
    theta_1(t) = 30 deg + 20 deg sin(t)
    theta_2(t) = 45 deg + 15 deg sin(2t)
    theta_3(t) = -20 deg + 10 deg cos(t)

Outputs
-------
outputs/phase7_trajectory.txt
outputs/phase7_uv_plot.png
outputs/phase7_uv_vs_time.png
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from camera import CameraMount, camera_pose_in_global  # noqa: E402
from cube import cube_vertex_world  # noqa: E402
from projection import CameraIntrinsics, project_world_point  # noqa: E402

T_TOTAL = 2.0 * np.pi
N_FRAMES = 200
T_VEC = np.linspace(0.0, T_TOTAL, N_FRAMES)

MOUNT = CameraMount(translation_e=(0.08, 0.0, 0.04), tilt_rad=np.deg2rad(-20.0))
INTRINSICS = CameraIntrinsics(fx=600.0, fy=600.0, cx=320.0, cy=240.0)
CUBE_SIDE = 0.20
VERTEX_SIGNS = (1, 1, 1)


def joint_angles_at(t_value: float) -> np.ndarray:
    """Return the 3-joint trajectory at time t."""

    return np.deg2rad(
        [
            30.0 + 20.0 * np.sin(t_value),
            45.0 + 15.0 * np.sin(2.0 * t_value),
            -20.0 + 10.0 * np.cos(t_value),
        ]
    )


def compute_trajectory() -> tuple[np.ndarray, np.ndarray, list[bool]]:
    """Track one cube vertex through the moving camera view."""

    u_values: list[float] = []
    v_values: list[float] = []
    in_views: list[bool] = []

    for t_value in T_VEC:
        angles = joint_angles_at(t_value)
        t_g_c = camera_pose_in_global(angles, mount=MOUNT)
        cube_center = (t_g_c @ np.array([0.0, 0.0, 1.20, 1.0], dtype=float))[:3]
        vertex = cube_vertex_world(cube_center, CUBE_SIDE, VERTEX_SIGNS)
        result = project_world_point(vertex, t_g_c, INTRINSICS)

        if result.in_front and not np.isnan(result.pixel).any():
            u_values.append(float(result.pixel[0]))
            v_values.append(float(result.pixel[1]))
        else:
            u_values.append(np.nan)
            v_values.append(np.nan)
        in_views.append(result.in_bounds)

    return np.array(u_values), np.array(v_values), in_views


def plot_uv(u_values: np.ndarray, v_values: np.ndarray, save_path: Path) -> None:
    """Plot the image-plane trajectory."""

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor("#1a1a1a")
    ax.set_facecolor("#0d0d0d")

    from matplotlib.patches import Rectangle

    ax.add_patch(
        Rectangle(
            (0, 0),
            INTRINSICS.width,
            INTRINSICS.height,
            edgecolor="white",
            facecolor="none",
            linewidth=1.5,
            linestyle="--",
        )
    )

    valid = ~np.isnan(u_values)
    scatter = ax.scatter(u_values[valid], v_values[valid], c=T_VEC[valid], cmap="plasma", s=8)
    colorbar = plt.colorbar(scatter, ax=ax)
    colorbar.set_label("t [s]", color="white")
    colorbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(colorbar.ax.yaxis.get_ticklabels(), color="white")

    if valid.any():
        first, last = np.where(valid)[0][0], np.where(valid)[0][-1]
        ax.plot(u_values[first], v_values[first], "g^", markersize=10, label="Start", zorder=5)
        ax.plot(u_values[last], v_values[last], "rs", markersize=10, label="End", zorder=5)

    ax.plot(
        INTRINSICS.cx,
        INTRINSICS.cy,
        "w+",
        markersize=14,
        markeredgewidth=2,
        label="Principal point",
    )
    ax.set_xlim(-20, INTRINSICS.width + 20)
    ax.set_ylim(INTRINSICS.height + 20, -20)
    ax.set_xlabel("u (px)", color="white")
    ax.set_ylabel("v (px)", color="white")
    ax.set_title("Phase 7 - Image-Plane Trajectory (vertex +,+,+)", color="white")
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("white")
    ax.legend(facecolor="#222222", labelcolor="white")
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def plot_vs_time(u_values: np.ndarray, v_values: np.ndarray, save_path: Path) -> None:
    """Plot pixel coordinates against time."""

    fig, (ax_u, ax_v) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    fig.patch.set_facecolor("#1a1a1a")

    for axis in (ax_u, ax_v):
        axis.set_facecolor("#0d0d0d")
        axis.tick_params(colors="white")
        for spine in axis.spines.values():
            spine.set_edgecolor("white")

    ax_u.plot(T_VEC, u_values, color="cyan", linewidth=1.8)
    ax_u.axhline(
        INTRINSICS.width,
        color="red",
        linewidth=0.8,
        linestyle="--",
        label=f"u_max={INTRINSICS.width}",
    )
    ax_u.set_ylabel("u (px)", color="white")
    ax_u.set_title("u(t) - horizontal pixel", color="white")
    ax_u.legend(facecolor="#222222", labelcolor="white")

    ax_v.plot(T_VEC, v_values, color="magenta", linewidth=1.8)
    ax_v.axhline(
        INTRINSICS.height,
        color="red",
        linewidth=0.8,
        linestyle="--",
        label=f"v_max={INTRINSICS.height}",
    )
    ax_v.set_ylabel("v (px)", color="white")
    ax_v.set_xlabel("t [s]", color="white")
    ax_v.set_title("v(t) - vertical pixel", color="white")
    ax_v.legend(facecolor="#222222", labelcolor="white")

    fig.suptitle("Phase 7 - Pixel Coordinates vs Time", color="white", fontsize=13)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def build_text_report(
    u_values: np.ndarray,
    v_values: np.ndarray,
    in_views: list[bool],
) -> str:
    """Build a sampled textual trajectory report."""

    lines = [
        "Phase 7: Image-Plane Trajectory",
        "",
        "theta_1(t) = 30 + 20*sin(t)  [deg]",
        "theta_2(t) = 45 + 15*sin(2t) [deg]",
        "theta_3(t) = -20 + 10*cos(t) [deg]",
        "Tracked vertex: (+L/2, +L/2, +L/2)",
        "",
        f"{'Frame':>5}  {'t':>7}  {'u (px)':>10}  {'v (px)':>10}  {'In view':>7}",
    ]
    lines.append("-" * 55)

    step = max(1, N_FRAMES // 20)
    for index in range(0, N_FRAMES, step):
        u_text = f"{u_values[index]:10.4f}" if not np.isnan(u_values[index]) else "       nan"
        v_text = f"{v_values[index]:10.4f}" if not np.isnan(v_values[index]) else "       nan"
        lines.append(
            f"{index:>5}  {T_VEC[index]:7.4f}  {u_text}  {v_text}  {str(in_views[index]):>7}"
        )

    lines.append("")
    percentage = 100.0 * sum(in_views) / len(in_views)
    lines.append(f"Frames in view: {sum(in_views)}/{N_FRAMES}  ({percentage:.1f}%)")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    output_dir = PROJECT_ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)

    u_values, v_values, in_views = compute_trajectory()
    report = build_text_report(u_values, v_values, in_views)
    (output_dir / "phase7_trajectory.txt").write_text(report, encoding="utf-8")
    print(report)

    plot_uv(u_values, v_values, output_dir / "phase7_uv_plot.png")
    plot_vs_time(u_values, v_values, output_dir / "phase7_uv_vs_time.png")

    print("Saved: outputs/phase7_trajectory.txt")
    print("Saved: outputs/phase7_uv_plot.png")
    print("Saved: outputs/phase7_uv_vs_time.png")


if __name__ == "__main__":
    main()
