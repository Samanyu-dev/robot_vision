"""Tests for Phase 6 Jacobian."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from jacobian import geometric_jacobian, joint_velocities_from_end_effector, manipulability  # noqa: E402


class JacobianTests(unittest.TestCase):
    def test_jacobian_shape(self) -> None:
        jacobian = geometric_jacobian(np.deg2rad([30.0, 45.0, -20.0]))
        self.assertEqual(jacobian.shape, (6, 3))

    def test_zero_pose_z0_is_world_z(self) -> None:
        jacobian = geometric_jacobian([0.0, 0.0, 0.0])
        np.testing.assert_allclose(jacobian[3:, 0], np.array([0.0, 0.0, 1.0]), atol=1e-12)

    def test_joint_velocity_projection_roundtrip(self) -> None:
        """J @ pinv(J) @ V equals J @ q_dot."""

        joint_angles = np.deg2rad([30.0, 45.0, -20.0])
        jacobian = geometric_jacobian(joint_angles)
        velocity = np.array([0.1, 0.05, 0.0, 0.0, 0.0, 0.2], dtype=float)
        q_dot = joint_velocities_from_end_effector(velocity, joint_angles)
        projected_velocity = jacobian @ np.linalg.pinv(jacobian) @ velocity
        np.testing.assert_allclose(jacobian @ q_dot, projected_velocity, atol=1e-10)

    def test_manipulability_positive(self) -> None:
        mu = manipulability(np.deg2rad([30.0, 45.0, -20.0]))
        self.assertGreater(mu, 0.0)

    def test_bad_velocity_input_raises(self) -> None:
        with self.assertRaises(ValueError):
            joint_velocities_from_end_effector([0.0, 0.0], [0.0, 0.0, 0.0])


if __name__ == "__main__":
    unittest.main()
