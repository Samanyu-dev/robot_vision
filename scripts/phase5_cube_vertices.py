"""Phase 5 - Project all 8 cube vertices into the image plane.

Outputs
-------
outputs/phase5_cube_vertices.txt
outputs/phase5_cube_image.png
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
from cube import CUBE_EDGES, cube_vertices_world  # noqa: E402
from projection import CameraIntrinsics, project_world_point  # noqa: E402


def project_cube(
    cube_center_g: np.ndarray,
    side_length: float,
    t_g_c: np.ndarray,
    intrinsics: CameraIntrinsics,
) -> tuple[np.ndarray, list[bool]]:
    """Project all 8 cube vertices and return pixels plus in-view flags."""

    vertices_g = cube_vertices_world(cube_center_g, side_length)
    pixels = np.full((8, 2), np.nan, dtype=float)
    visible: list[bool] = []

    for index, vertex in enumerate(vertices_g):
        result = project_world_point(vertex, t_g_c, intrinsics)
        if result.in_front:
            pixels[index] = result.pixel
        visible.append(result.in_front and result.in_bounds)

    return pixels, visible


def draw_camera_view(
    pixels: np.ndarray,
    visible: list[bool],
    intrinsics: CameraIntrinsics,
    save_path: Path,
) -> None:
    """Render a 640 x 480 camera-view plot and save it."""

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor("#111111")
    ax.set_facecolor("#111111")
    ax.set_xlim(0, intrinsics.width)
    ax.set_ylim(intrinsics.height, 0)
    ax.set_aspect("equal")
    ax.set_title("Phase 5 - Camera View: Projected Cube", color="white")
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("white")

    ax.plot(
        intrinsics.cx,
        intrinsics.cy,
        "r+",
        markersize=14,
        markeredgewidth=2,
        label="Principal point",
    )

    for index0, index1 in CUBE_EDGES:
        if not np.isnan(pixels[index0]).any() and not np.isnan(pixels[index1]).any():
            ax.plot(
                [pixels[index0, 0], pixels[index1, 0]],
                [pixels[index0, 1], pixels[index1, 1]],
                color="deepskyblue",
                linewidth=1.5,
            )

    for index, (pixel, is_visible) in enumerate(zip(pixels, visible)):
        if not np.isnan(pixel).any():
            color = "lime" if is_visible else "orange"
            ax.plot(pixel[0], pixel[1], "o", color=color, markersize=7)
            ax.text(pixel[0] + 4, pixel[1] - 4, str(index), color=color, fontsize=8)

    if not all(visible):
        ax.text(
            intrinsics.width / 2.0,
            intrinsics.height / 2.0,
            "SOME VERTICES OUT OF VIEW",
            color="red",
            fontsize=13,
            fontweight="bold",
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.4", fc="black", alpha=0.7),
        )

    ax.legend(loc="upper right", facecolor="#222222", labelcolor="white")
    ax.set_xlabel("u (px)", color="white")
    ax.set_ylabel("v (px)", color="white")
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def build_report(
    joint_angles: np.ndarray,
    cube_center_g: np.ndarray,
    side_length: float,
    pixels: np.ndarray,
    visible: list[bool],
) -> str:
    """Build a stable text report for all cube vertices."""

    vertices_g = cube_vertices_world(cube_center_g, side_length)
    lines: list[str] = ["Phase 5: Projected Cube Vertices", ""]
    lines.append(f"Joint angles [deg]: {np.rad2deg(joint_angles).tolist()}")
    lines.append(f"Cube center P_center_G [m]: {cube_center_g.tolist()}")
    lines.append(f"Side length [m]: {side_length}")
    lines.append("")
    lines.append(
        f"{'Vtx':>3}  {'World X':>9} {'World Y':>9} {'World Z':>9}  "
        f"{'u (px)':>9} {'v (px)':>9}  {'In view':>7}"
    )
    lines.append("-" * 75)

    for index, (vertex_g, pixel, is_visible) in enumerate(zip(vertices_g, pixels, visible)):
        u_text = f"{pixel[0]:9.4f}" if not np.isnan(pixel[0]) else "      nan"
        v_text = f"{pixel[1]:9.4f}" if not np.isnan(pixel[1]) else "      nan"
        lines.append(
            f"{index:>3}  {vertex_g[0]:9.4f} {vertex_g[1]:9.4f} {vertex_g[2]:9.4f}  "
            f"{u_text} {v_text}  {str(is_visible):>7}"
        )

    lines.append("")
    lines.append(f"All vertices in view: {all(visible)}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    joint_angles = np.deg2rad([30.0, 45.0, -20.0])
    mount = CameraMount(translation_e=(0.08, 0.0, 0.04), tilt_rad=np.deg2rad(-20.0))
    intrinsics = CameraIntrinsics(fx=600.0, fy=600.0, cx=320.0, cy=240.0)
    side_length = 0.20

    t_g_c = camera_pose_in_global(joint_angles, mount=mount)
    cube_center_g = (t_g_c @ np.array([0.0, 0.0, 1.20, 1.0], dtype=float))[:3]

    pixels, visible = project_cube(cube_center_g, side_length, t_g_c, intrinsics)
    report = build_report(joint_angles, cube_center_g, side_length, pixels, visible)

    output_dir = PROJECT_ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "phase5_cube_vertices.txt").write_text(report, encoding="utf-8")
    draw_camera_view(pixels, visible, intrinsics, output_dir / "phase5_cube_image.png")

    print(report)
    print("Saved: outputs/phase5_cube_vertices.txt")
    print("Saved: outputs/phase5_cube_image.png")


if __name__ == "__main__":
    main()
