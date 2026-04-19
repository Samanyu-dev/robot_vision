"""Tests for cube point helpers."""

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
from cube import cube_vertex_world, cube_vertices_local, cube_vertices_world  # noqa: E402
from projection import project_world_point, transform_world_to_camera  # noqa: E402


class CubeTests(unittest.TestCase):
    def test_cube_vertices_local_shape_and_extent(self) -> None:
        vertices = cube_vertices_local(0.2)
        self.assertEqual(vertices.shape, (8, 3))
        self.assertAlmostEqual(vertices.min(), -0.1)
        self.assertAlmostEqual(vertices.max(), 0.1)

    def test_cube_vertices_world_translate_local_vertices(self) -> None:
        center = np.array([1.0, 2.0, 3.0])
        local = cube_vertices_local(0.2)
        world = cube_vertices_world(center, 0.2)
        np.testing.assert_allclose(world, local + center)

    def test_cube_vertex_world_uses_signs(self) -> None:
        vertex = cube_vertex_world([1.0, 2.0, 3.0], 0.2, signs=(1, -1, 1))
        np.testing.assert_allclose(vertex, np.array([1.1, 1.9, 3.1]))

    def test_cube_vertex_world_validates_signs(self) -> None:
        with self.assertRaises(ValueError):
            cube_vertex_world([0.0, 0.0, 0.0], 0.2, signs=(0, 1, 1))

    def test_phase4_selected_vertex_projects_inside_image(self) -> None:
        joint_angles = np.deg2rad([30.0, 45.0, -20.0])
        mount = CameraMount(translation_e=(0.08, 0.0, 0.04), tilt_rad=np.deg2rad(-20.0))
        t_g_c = camera_pose_in_global(joint_angles, mount=mount)
        cube_center_g = (t_g_c @ np.array([0.0, 0.0, 1.20, 1.0]))[:3]
        vertex_g = cube_vertex_world(cube_center_g, 0.2, signs=(1, 1, 1))
        vertex_c = transform_world_to_camera(vertex_g, t_g_c)
        result = project_world_point(vertex_g, t_g_c)

        self.assertTrue(result.in_front)
        self.assertTrue(result.in_bounds)
        np.testing.assert_allclose(vertex_c[3], 1.0, atol=1e-12)
        np.testing.assert_allclose(result.pixel, np.array([336.061926, 228.642503]), atol=1e-6)


if __name__ == "__main__":
    unittest.main()
