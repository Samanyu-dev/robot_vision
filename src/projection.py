"""World-to-camera and pinhole projection utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class CameraIntrinsics:
    """Pinhole camera intrinsic parameters."""

    fx: float = 600.0
    fy: float = 600.0
    cx: float = 320.0
    cy: float = 240.0
    width: int = 640
    height: int = 480


@dataclass(frozen=True)
class ProjectionResult:
    """Projected pixel plus intermediate camera-frame data."""

    pixel: np.ndarray
    camera_point: np.ndarray
    in_front: bool
    in_bounds: bool


def intrinsic_matrix(intrinsics: CameraIntrinsics = CameraIntrinsics()) -> np.ndarray:
    """Return the 3 x 3 camera intrinsic matrix K."""

    return np.array(
        [
            [intrinsics.fx, 0.0, intrinsics.cx],
            [0.0, intrinsics.fy, intrinsics.cy],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


def as_homogeneous_point(point: Sequence[float]) -> np.ndarray:
    """Return a 4D homogeneous point from a 3D or 4D point."""

    point_array = np.asarray(point, dtype=float)
    if point_array.shape == (3,):
        return np.array([point_array[0], point_array[1], point_array[2], 1.0])
    if point_array.shape == (4,):
        if np.isclose(point_array[3], 0.0):
            raise ValueError("homogeneous point w component must be nonzero")
        return point_array
    raise ValueError(f"point must have shape (3,) or (4,), got {point_array.shape}")


def world_to_camera_transform(camera_transform_g_c: np.ndarray) -> np.ndarray:
    """Return T_CG from T_GC."""

    camera_transform_g_c = np.asarray(camera_transform_g_c, dtype=float)
    if camera_transform_g_c.shape != (4, 4):
        raise ValueError(
            "camera_transform_g_c must have shape (4, 4), "
            f"got {camera_transform_g_c.shape}"
        )
    return np.linalg.inv(camera_transform_g_c)


def world_to_camera_extrinsic(camera_transform_g_c: np.ndarray) -> np.ndarray:
    """Return the 3 x 4 world-to-camera extrinsic matrix [R | t]."""

    return world_to_camera_transform(camera_transform_g_c)[:3, :]


def transform_world_to_camera(
    world_point: Sequence[float],
    camera_transform_g_c: np.ndarray,
) -> np.ndarray:
    """Transform a world point P_G into camera coordinates P_C."""

    point_g = as_homogeneous_point(world_point)
    point_c = world_to_camera_transform(camera_transform_g_c) @ point_g
    if not np.isclose(point_c[3], 1.0):
        point_c = point_c / point_c[3]
    return point_c


def project_camera_point(
    camera_point: Sequence[float],
    intrinsics: CameraIntrinsics = CameraIntrinsics(),
) -> ProjectionResult:
    """Project a camera-frame 3D point onto the image plane."""

    point_c = as_homogeneous_point(camera_point)
    x_c, y_c, z_c, _ = point_c
    in_front = bool(z_c > 0.0)

    if not in_front:
        pixel = np.array([np.nan, np.nan], dtype=float)
        return ProjectionResult(
            pixel=pixel,
            camera_point=point_c,
            in_front=False,
            in_bounds=False,
        )

    u = intrinsics.fx * x_c / z_c + intrinsics.cx
    v = intrinsics.fy * y_c / z_c + intrinsics.cy
    pixel = np.array([u, v], dtype=float)
    in_bounds = bool(0.0 <= u <= intrinsics.width and 0.0 <= v <= intrinsics.height)

    return ProjectionResult(
        pixel=pixel,
        camera_point=point_c,
        in_front=True,
        in_bounds=in_bounds,
    )


def project_world_point(
    world_point: Sequence[float],
    camera_transform_g_c: np.ndarray,
    intrinsics: CameraIntrinsics = CameraIntrinsics(),
) -> ProjectionResult:
    """Project a world-frame 3D point through T_GC and K."""

    point_c = transform_world_to_camera(world_point, camera_transform_g_c)
    return project_camera_point(point_c, intrinsics)


def camera_matrix(
    camera_transform_g_c: np.ndarray,
    intrinsics: CameraIntrinsics = CameraIntrinsics(),
) -> np.ndarray:
    """Return the 3 x 4 matrix K [R | t] for world-to-image mapping."""

    return intrinsic_matrix(intrinsics) @ world_to_camera_extrinsic(camera_transform_g_c)

