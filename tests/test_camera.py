"""Tests for Phase 2 camera extrinsics."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from camera import (  # noqa: E402
    CameraMount,
    camera_mount_transform,
    camera_pose_from_end_effector,
    camera_pose_in_global,
    homogeneous_transform,
    rotation_y,
)
from kinematics import forward_kinematics  # noqa: E402


class CameraExtrinsicsTests(unittest.TestCase):
    def test_homogeneous_transform(self) -> None:
        rotation = np.eye(3)
        translation = np.array([1.0, 2.0, 3.0])
        transform = homogeneous_transform(rotation, translation)
        np.testing.assert_allclose(transform[:3, :3], rotation)
        np.testing.assert_allclose(transform[:3, 3], translation)
        np.testing.assert_allclose(transform[3], np.array([0.0, 0.0, 0.0, 1.0]))

    def test_camera_alignment_points_optical_axis_along_end_effector_x(self) -> None:
        mount = CameraMount(translation_e=(0.0, 0.0, 0.0), tilt_rad=0.0)
        transform = camera_mount_transform(mount)
        optical_axis_in_e = transform[:3, 2]
        np.testing.assert_allclose(optical_axis_in_e, np.array([1.0, 0.0, 0.0]), atol=1e-12)

    def test_camera_mount_rotation_is_orthonormal(self) -> None:
        transform = camera_mount_transform()
        rotation = transform[:3, :3]
        np.testing.assert_allclose(rotation.T @ rotation, np.eye(3), atol=1e-12)
        self.assertAlmostEqual(np.linalg.det(rotation), 1.0)

    def test_camera_pose_matches_manual_chain(self) -> None:
        joint_angles = np.deg2rad([30.0, 45.0, -20.0])
        mount = CameraMount(translation_e=(0.08, 0.0, 0.04), tilt_rad=np.deg2rad(-20.0))
        t_b_e = forward_kinematics(joint_angles).end_effector_transform
        t_e_c = camera_mount_transform(mount)
        expected = t_b_e @ t_e_c
        actual = camera_pose_in_global(joint_angles, mount=mount)
        np.testing.assert_allclose(actual, expected)

    def test_camera_pose_from_end_effector_validates_transform_shape(self) -> None:
        with self.assertRaises(ValueError):
            camera_pose_from_end_effector(np.eye(3))

    def test_rotation_y_maps_z_to_x_at_positive_half_pi(self) -> None:
        rotated_z = rotation_y(np.pi / 2.0) @ np.array([0.0, 0.0, 1.0])
        np.testing.assert_allclose(rotated_z, np.array([1.0, 0.0, 0.0]), atol=1e-12)


if __name__ == "__main__":
    unittest.main()
