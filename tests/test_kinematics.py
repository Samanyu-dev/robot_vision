"""Tests for Phase 1 kinematics."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from kinematics import (  # noqa: E402
    DEFAULT_DH_PARAMS,
    as_joint_array,
    dh_transform,
    end_effector_position,
    forward_kinematics,
)


class KinematicsTests(unittest.TestCase):
    def test_dh_transform_zero_planar_link(self) -> None:
        transform = dh_transform(theta=0.0, d=0.0, a=2.0, alpha=0.0)
        expected = np.array(
            [
                [1.0, 0.0, 0.0, 2.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )
        np.testing.assert_allclose(transform, expected, atol=1e-12)

    def test_forward_kinematics_returns_base_and_three_link_frames(self) -> None:
        result = forward_kinematics([0.0, 0.0, 0.0])
        self.assertEqual(len(result.transforms), 4)
        np.testing.assert_allclose(result.transforms[0], np.eye(4), atol=1e-12)

    def test_zero_pose_end_effector_position(self) -> None:
        result = forward_kinematics([0.0, 0.0, 0.0])
        expected = np.array(
            [
                DEFAULT_DH_PARAMS[1].a + DEFAULT_DH_PARAMS[2].a,
                0.0,
                DEFAULT_DH_PARAMS[0].d,
            ]
        )
        np.testing.assert_allclose(result.end_effector_transform[:3, 3], expected)

    def test_helper_position_matches_forward_kinematics(self) -> None:
        joint_angles = np.deg2rad([30.0, 45.0, -20.0])
        expected = forward_kinematics(joint_angles).end_effector_transform[:3, 3]
        actual = end_effector_position(joint_angles)
        np.testing.assert_allclose(actual, expected)

    def test_joint_angle_validation(self) -> None:
        with self.assertRaises(ValueError):
            as_joint_array([0.0, 1.0])


if __name__ == "__main__":
    unittest.main()

