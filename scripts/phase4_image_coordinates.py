"""Run the Phase 4 image-coordinate calculation for one cube vertex."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from camera import CameraMount, camera_pose_in_global  # noqa: E402
from cube import cube_vertex_world  # noqa: E402
from kinematics import forward_kinematics  # noqa: E402
from projection import (  # noqa: E402
    CameraIntrinsics,
    intrinsic_matrix,
    project_world_point,
    transform_world_to_camera,
)


def format_matrix(matrix: np.ndarray) -> str:
    """Format a matrix for a stable text artifact."""

    return np.array2string(matrix, precision=6, suppress_small=True)


def build_report() -> str:
    """Build the text output for the Phase 4 numerical example."""

    joint_angles = np.deg2rad([30.0, 45.0, -20.0])
    mount = CameraMount(translation_e=(0.08, 0.0, 0.04), tilt_rad=np.deg2rad(-20.0))
    intrinsics = CameraIntrinsics(fx=600.0, fy=600.0, cx=320.0, cy=240.0)
    cube_side_length = 0.20
    selected_vertex_signs = (1, 1, 1)

    t_b_e = forward_kinematics(joint_angles).end_effector_transform
    t_g_c = camera_pose_in_global(joint_angles, mount=mount)

    visible_center_c = np.array([0.0, 0.0, 1.20, 1.0])
    cube_center_g = (t_g_c @ visible_center_c)[:3]
    vertex_g = cube_vertex_world(
        center=cube_center_g,
        side_length=cube_side_length,
        signs=selected_vertex_signs,
    )
    vertex_c = transform_world_to_camera(vertex_g, t_g_c)
    projection = project_world_point(vertex_g, t_g_c, intrinsics)

    lines: list[str] = []
    lines.append("Phase 4: Image Coordinates for One Cube Vertex")
    lines.append("")
    lines.append("Joint angles:")
    lines.append(f"degrees: {np.array2string(np.rad2deg(joint_angles), precision=3)}")
    lines.append(f"radians: {np.array2string(joint_angles, precision=6)}")
    lines.append("")
    lines.append("Camera intrinsics K:")
    lines.append(format_matrix(intrinsic_matrix(intrinsics)))
    lines.append("")
    lines.append("T_BE:")
    lines.append(format_matrix(t_b_e))
    lines.append("")
    lines.append("T_GC:")
    lines.append(format_matrix(t_g_c))
    lines.append("")
    lines.append("Cube setup:")
    lines.append(f"side length [m]: {cube_side_length:.6f}")
    lines.append(
        "center selected 1.20 m along camera +Z axis, then expressed in world frame"
    )
    lines.append(f"cube center P_center_G [m]: {np.array2string(cube_center_g, precision=6)}")
    lines.append(f"selected vertex signs: {selected_vertex_signs}")
    lines.append("")
    lines.append("Selected cube vertex in world frame P_G [m]:")
    lines.append(np.array2string(vertex_g, precision=6))
    lines.append("")
    lines.append("Selected cube vertex in camera frame P_C [m]:")
    lines.append(np.array2string(vertex_c, precision=6))
    lines.append("")
    lines.append("Projection equations:")
    lines.append("u = fx * X_C / Z_C + cx")
    lines.append("v = fy * Y_C / Z_C + cy")
    lines.append("")
    lines.append("Pixel coordinate [u, v]:")
    lines.append(np.array2string(projection.pixel, precision=6))
    lines.append("")
    lines.append(f"In front of camera: {projection.in_front}")
    lines.append(f"Inside 640 x 480 image bounds: {projection.in_bounds}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    report = build_report()
    output_path = PROJECT_ROOT / "outputs" / "phase4_image_coordinates.txt"
    output_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"Saved: {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()

