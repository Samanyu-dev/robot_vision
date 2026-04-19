"""Tests for Phase 3 projection utilities."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from camera import CameraMount, camera_pose_in_global  # noqa: E402
from projection import (  # noqa: E402
    CameraIntrinsics,
    as_homogeneous_point,
    camera_matrix,
    intrinsic_matrix,
    project_camera_point,
    project_world_point,
    transform_world_to_camera,
    world_to_camera_extrinsic,
    world_to_camera_transform,
)


class ProjectionTests(unittest.TestCase):
    def test_intrinsic_matrix(self) -> None:
        intrinsics = CameraIntrinsics(fx=600.0, fy=610.0, cx=320.0, cy=240.0)
        expected = np.array(
            [
                [600.0, 0.0, 320.0],
                [0.0, 610.0, 240.0],
                [0.0, 0.0, 1.0],
            ]
        )
        np.testing.assert_allclose(intrinsic_matrix(intrinsics), expected)

    def test_as_homogeneous_point_accepts_3d_and_4d_points(self) -> None:
        np.testing.assert_allclose(
            as_homogeneous_point([1.0, 2.0, 3.0]),
            np.array([1.0, 2.0, 3.0, 1.0]),
        )
        np.testing.assert_allclose(
            as_homogeneous_point([1.0, 2.0, 3.0, 1.0]),
            np.array([1.0, 2.0, 3.0, 1.0]),
        )

    def test_world_to_camera_round_trip(self) -> None:
        joint_angles = np.deg2rad([30.0, 45.0, -20.0])
        mount = CameraMount(translation_e=(0.08, 0.0, 0.04), tilt_rad=np.deg2rad(-20.0))
        t_g_c = camera_pose_in_global(joint_angles, mount=mount)
        point_c = np.array([0.05, -0.03, 1.0, 1.0])
        point_g = t_g_c @ point_c
        recovered_c = transform_world_to_camera(point_g, t_g_c)
        np.testing.assert_allclose(recovered_c, point_c, atol=1e-12)

    def test_project_camera_point(self) -> None:
        intrinsics = CameraIntrinsics(fx=600.0, fy=600.0, cx=320.0, cy=240.0)
        result = project_camera_point([0.05, -0.03, 1.0], intrinsics)
        np.testing.assert_allclose(result.pixel, np.array([350.0, 222.0]))
        self.assertTrue(result.in_front)
        self.assertTrue(result.in_bounds)

    def test_project_world_point_matches_camera_point_projection(self) -> None:
        joint_angles = np.deg2rad([30.0, 45.0, -20.0])
        mount = CameraMount(translation_e=(0.08, 0.0, 0.04), tilt_rad=np.deg2rad(-20.0))
        t_g_c = camera_pose_in_global(joint_angles, mount=mount)
        point_c = np.array([0.05, -0.03, 1.0, 1.0])
        point_g = t_g_c @ point_c
        result = project_world_point(point_g, t_g_c)
        np.testing.assert_allclose(result.pixel, np.array([350.0, 222.0]), atol=1e-12)

    def test_point_behind_camera_is_not_projected(self) -> None:
        result = project_camera_point([0.0, 0.0, -1.0])
        self.assertFalse(result.in_front)
        self.assertFalse(result.in_bounds)
        self.assertTrue(np.isnan(result.pixel).all())

    def test_camera_matrix_matches_k_times_extrinsic(self) -> None:
        t_g_c = camera_pose_in_global(np.deg2rad([30.0, 45.0, -20.0]))
        expected = intrinsic_matrix() @ world_to_camera_extrinsic(t_g_c)
        actual = camera_matrix(t_g_c)
        np.testing.assert_allclose(actual, expected)

    def test_world_to_camera_transform_validates_shape(self) -> None:
        with self.assertRaises(ValueError):
            world_to_camera_transform(np.eye(3))


if __name__ == "__main__":
    unittest.main()

