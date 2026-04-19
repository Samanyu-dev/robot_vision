"""Run the Phase 2 camera extrinsics numerical example."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from camera import CameraMount, camera_mount_transform, camera_pose_in_global  # noqa: E402
from kinematics import forward_kinematics  # noqa: E402


def format_matrix(matrix: np.ndarray) -> str:
    """Format a matrix for a stable text artifact."""

    return np.array2string(matrix, precision=6, suppress_small=True)


def build_report() -> str:
    """Build the text output for the Phase 2 numerical example."""

    joint_angles = np.deg2rad([30.0, 45.0, -20.0])
    mount = CameraMount(translation_e=(0.08, 0.0, 0.04), tilt_rad=np.deg2rad(-20.0))
    t_b_e = forward_kinematics(joint_angles).end_effector_transform
    t_e_c = camera_mount_transform(mount)
    t_g_c = camera_pose_in_global(joint_angles, mount=mount)

    lines: list[str] = []
    lines.append("Phase 2: Camera Extrinsics Numerical Example")
    lines.append("")
    lines.append("Joint angles:")
    lines.append(f"degrees: {np.array2string(np.rad2deg(joint_angles), precision=3)}")
    lines.append(f"radians: {np.array2string(joint_angles, precision=6)}")
    lines.append("")
    lines.append("Camera mount:")
    lines.append(
        "translation_e [m]: "
        f"{np.array2string(np.asarray(mount.translation_e), precision=6)}"
    )
    lines.append(f"tilt about local camera x-axis [deg]: {np.rad2deg(mount.tilt_rad):.6f}")
    lines.append("")
    lines.append("T_BE:")
    lines.append(format_matrix(t_b_e))
    lines.append("")
    lines.append("T_EC:")
    lines.append(format_matrix(t_e_c))
    lines.append("")
    lines.append("T_GC = T_BE * T_EC:")
    lines.append(format_matrix(t_g_c))
    lines.append("")
    lines.append("Camera origin in global/base frame [m]:")
    lines.append(np.array2string(t_g_c[:3, 3], precision=6))
    lines.append("")
    lines.append("Camera optical axis +Z_C in global/base frame:")
    lines.append(np.array2string(t_g_c[:3, 2], precision=6))
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    report = build_report()
    output_path = PROJECT_ROOT / "outputs" / "phase2_camera_extrinsics.txt"
    output_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"Saved: {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()

