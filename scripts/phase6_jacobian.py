"""Phase 6 - Jacobian derivation and joint velocity calculation.

Outputs
-------
outputs/phase6_jacobian.txt
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from jacobian import geometric_jacobian, joint_velocities_from_end_effector, manipulability  # noqa: E402
from kinematics import forward_kinematics  # noqa: E402


def build_report() -> str:
    """Build the numerical Phase 6 report."""

    joint_angles = np.deg2rad([30.0, 45.0, -20.0])
    result = forward_kinematics(joint_angles)
    jacobian = geometric_jacobian(joint_angles)
    desired_velocity = np.array([0.10, 0.05, 0.0, 0.0, 0.0, 0.3], dtype=float)
    q_dot = joint_velocities_from_end_effector(desired_velocity, joint_angles)
    mu = manipulability(joint_angles)

    lines: list[str] = ["Phase 6: Jacobian and Joint Velocity", ""]
    lines.append(f"Joint angles [deg]: {np.rad2deg(joint_angles).tolist()}")
    lines.append("")
    lines.append("Frame origins o_0 ... o_3 [m]:")
    for index, origin in enumerate(result.origins):
        lines.append(f"  o_{index} = {np.array2string(origin, precision=6)}")
    lines.append("")
    lines.append("Z-axes z_0 ... z_3:")
    for index, axis in enumerate(result.z_axes):
        lines.append(f"  z_{index} = {np.array2string(axis, precision=6)}")
    lines.append("")
    lines.append("Geometric Jacobian J (6 x 3):")
    lines.append("  Rows 0-2 : linear   (z_{i-1} x (o_E - o_{i-1}))")
    lines.append("  Rows 3-5 : angular  (z_{i-1})")
    lines.append("")
    lines.append(np.array2string(jacobian, precision=6, suppress_small=True))
    lines.append("")
    lines.append(f"Yoshikawa manipulability: {mu:.6f}")
    lines.append(f"Condition number of J:    {np.linalg.cond(jacobian):.4f}")
    lines.append("")
    lines.append("Joint velocity calculation:")
    lines.append(f"  Desired V  = {desired_velocity.tolist()}")
    lines.append("  q_dot      = pinv(J) @ V")
    lines.append(f"  q_dot      = {np.array2string(q_dot, precision=6)} [rad/s]")
    lines.append("")
    lines.append("Note: J is 6 x 3 (rank 3). pinv(J) gives the minimum-norm q_dot")
    lines.append("that minimises ||J q_dot - V||. Full 6-DOF recovery needs a 6 x 6 J.")
    lines.append("")
    projected_velocity = jacobian @ np.linalg.pinv(jacobian) @ desired_velocity
    lines.append(
        f"Projection of V onto col(J): {np.array2string(projected_velocity, precision=6)}"
    )
    lines.append(f"J @ q_dot:                   {np.array2string(jacobian @ q_dot, precision=6)}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    report = build_report()
    output_dir = PROJECT_ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "phase6_jacobian.txt").write_text(report, encoding="utf-8")
    print(report)
    print("Saved: outputs/phase6_jacobian.txt")


if __name__ == "__main__":
    main()
