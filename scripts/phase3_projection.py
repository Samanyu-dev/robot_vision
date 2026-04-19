"""Run the Phase 3 world-to-image projection numerical example."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from camera import CameraMount, camera_pose_in_global  # noqa: E402
from projection import (  # noqa: E402
    CameraIntrinsics,
    camera_matrix,
    intrinsic_matrix,
    project_world_point,
    transform_world_to_camera,
    world_to_camera_extrinsic,
    world_to_camera_transform,
)


def format_matrix(matrix: np.ndarray) -> str:
    """Format a matrix for a stable text artifact."""

    return np.array2string(matrix, precision=6, suppress_small=True)


def build_report() -> str:
    """Build the text output for the Phase 3 numerical example."""

    joint_angles = np.deg2rad([30.0, 45.0, -20.0])
    mount = CameraMount(translation_e=(0.08, 0.0, 0.04), tilt_rad=np.deg2rad(-20.0))
    intrinsics = CameraIntrinsics(fx=600.0, fy=600.0, cx=320.0, cy=240.0)
    t_g_c = camera_pose_in_global(joint_angles, mount=mount)
    t_c_g = world_to_camera_transform(t_g_c)

    sample_point_c = np.array([0.05, -0.03, 1.0, 1.0])
    sample_point_g = t_g_c @ sample_point_c
    recovered_point_c = transform_world_to_camera(sample_point_g, t_g_c)
    projection = project_world_point(sample_point_g, t_g_c, intrinsics)

    lines: list[str] = []
    lines.append("Phase 3: World-to-Image Projection Numerical Example")
    lines.append("")
    lines.append("Joint angles:")
    lines.append(f"degrees: {np.array2string(np.rad2deg(joint_angles), precision=3)}")
    lines.append("")
    lines.append("Camera intrinsics K:")
    lines.append(format_matrix(intrinsic_matrix(intrinsics)))
    lines.append("")
    lines.append("T_GC:")
    lines.append(format_matrix(t_g_c))
    lines.append("")
    lines.append("T_CG = inv(T_GC):")
    lines.append(format_matrix(t_c_g))
    lines.append("")
    lines.append("[R | t] world-to-camera extrinsic:")
    lines.append(format_matrix(world_to_camera_extrinsic(t_g_c)))
    lines.append("")
    lines.append("Camera matrix K [R | t]:")
    lines.append(format_matrix(camera_matrix(t_g_c, intrinsics)))
    lines.append("")
    lines.append("Chosen visible point in camera frame P_C:")
    lines.append(np.array2string(sample_point_c, precision=6))
    lines.append("")
    lines.append("Equivalent world point P_G = T_GC * P_C:")
    lines.append(np.array2string(sample_point_g, precision=6))
    lines.append("")
    lines.append("Recovered camera point inv(T_GC) * P_G:")
    lines.append(np.array2string(recovered_point_c, precision=6))
    lines.append("")
    lines.append("Pixel projection [u, v]:")
    lines.append(np.array2string(projection.pixel, precision=6))
    lines.append("")
    lines.append(f"In front of camera: {projection.in_front}")
    lines.append(f"Inside 640 x 480 image bounds: {projection.in_bounds}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    report = build_report()
    output_path = PROJECT_ROOT / "outputs" / "phase3_projection.txt"
    output_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"Saved: {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()

