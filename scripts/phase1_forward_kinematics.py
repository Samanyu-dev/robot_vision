"""Run the Phase 1 forward kinematics numerical example."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from kinematics import DEFAULT_DH_PARAMS, forward_kinematics  # noqa: E402


def format_matrix(matrix: np.ndarray) -> str:
    """Format a matrix for a stable text artifact."""

    return np.array2string(matrix, precision=6, suppress_small=True)


def build_report() -> str:
    """Build the text output for the Phase 1 numerical example."""

    joint_angles = np.deg2rad([30.0, 45.0, -20.0])
    result = forward_kinematics(joint_angles)
    lines: list[str] = []

    lines.append("Phase 1: Forward Kinematics Numerical Example")
    lines.append("")
    lines.append("DH parameters:")
    lines.append("joint, theta_variable, d, a, alpha")
    for index, link in enumerate(DEFAULT_DH_PARAMS, start=1):
        lines.append(
            f"{index}, theta_{index}, {link.d:.6f}, "
            f"{link.a:.6f}, {link.alpha:.6f}"
        )

    lines.append("")
    lines.append("Joint angles:")
    lines.append(f"degrees: {np.array2string(np.rad2deg(joint_angles), precision=3)}")
    lines.append(f"radians: {np.array2string(joint_angles, precision=6)}")

    for index, transform in enumerate(result.transforms[1:], start=1):
        lines.append("")
        lines.append(f"T_B{index}:")
        lines.append(format_matrix(transform))

    lines.append("")
    lines.append("End-effector pose T_BE:")
    lines.append(format_matrix(result.end_effector_transform))
    lines.append("")
    lines.append("End-effector position [m]:")
    lines.append(np.array2string(result.end_effector_transform[:3, 3], precision=6))
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    report = build_report()
    output_path = PROJECT_ROOT / "outputs" / "phase1_forward_kinematics.txt"
    output_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"Saved: {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
