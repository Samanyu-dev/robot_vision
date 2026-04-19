"""Camera extrinsics for an end-effector mounted pinhole camera."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np

from kinematics import DEFAULT_DH_PARAMS, DHLink, forward_kinematics


DEFAULT_CAMERA_TRANSLATION_E: tuple[float, float, float] = (0.08, 0.0, 0.04)
DEFAULT_CAMERA_TILT_RAD: float = np.deg2rad(-20.0)


@dataclass(frozen=True)
class CameraMount:
    """Rigid camera pose relative to the end-effector frame."""

    translation_e: tuple[float, float, float] = DEFAULT_CAMERA_TRANSLATION_E
    tilt_rad: float = DEFAULT_CAMERA_TILT_RAD


def rotation_x(angle_rad: float) -> np.ndarray:
    """Return a 3D rotation matrix about the x-axis."""

    cos_angle = np.cos(angle_rad)
    sin_angle = np.sin(angle_rad)
    return np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, cos_angle, -sin_angle],
            [0.0, sin_angle, cos_angle],
        ],
        dtype=float,
    )


def rotation_y(angle_rad: float) -> np.ndarray:
    """Return a 3D rotation matrix about the y-axis."""

    cos_angle = np.cos(angle_rad)
    sin_angle = np.sin(angle_rad)
    return np.array(
        [
            [cos_angle, 0.0, sin_angle],
            [0.0, 1.0, 0.0],
            [-sin_angle, 0.0, cos_angle],
        ],
        dtype=float,
    )


def homogeneous_transform(rotation: np.ndarray, translation: Sequence[float]) -> np.ndarray:
    """Build a homogeneous transform from rotation and translation."""

    rotation = np.asarray(rotation, dtype=float)
    translation = np.asarray(translation, dtype=float)

    if rotation.shape != (3, 3):
        raise ValueError(f"rotation must have shape (3, 3), got {rotation.shape}")
    if translation.shape != (3,):
        raise ValueError(f"translation must have shape (3,), got {translation.shape}")

    transform = np.eye(4, dtype=float)
    transform[:3, :3] = rotation
    transform[:3, 3] = translation
    return transform


def camera_mount_transform(mount: CameraMount = CameraMount()) -> np.ndarray:
    """Return T_EC, the camera frame pose relative to the end-effector.

    The alignment makes the camera optical axis +Z_C point along +X_E.
    The tilt is then applied about the local camera x-axis.
    """

    optical_axis_alignment = rotation_y(np.pi / 2.0)
    local_tilt = rotation_x(mount.tilt_rad)
    rotation_e_c = optical_axis_alignment @ local_tilt
    return homogeneous_transform(rotation_e_c, mount.translation_e)


def camera_pose_from_end_effector(
    end_effector_transform: np.ndarray,
    camera_transform_e_c: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Compute T_GC from a known T_GE or T_BE end-effector pose."""

    end_effector_transform = np.asarray(end_effector_transform, dtype=float)
    if end_effector_transform.shape != (4, 4):
        raise ValueError(
            "end_effector_transform must have shape (4, 4), "
            f"got {end_effector_transform.shape}"
        )

    if camera_transform_e_c is None:
        camera_transform_e_c = camera_mount_transform()

    camera_transform_e_c = np.asarray(camera_transform_e_c, dtype=float)
    if camera_transform_e_c.shape != (4, 4):
        raise ValueError(
            "camera_transform_e_c must have shape (4, 4), "
            f"got {camera_transform_e_c.shape}"
        )

    return end_effector_transform @ camera_transform_e_c


def camera_pose_in_global(
    joint_angles: Sequence[float],
    mount: CameraMount = CameraMount(),
    base_transform_g_b: Optional[np.ndarray] = None,
    dh_params: Sequence[DHLink] = DEFAULT_DH_PARAMS,
) -> np.ndarray:
    """Compute T_GC from joint angles and a fixed wrist camera mount."""

    if base_transform_g_b is None:
        base_transform_g_b = np.eye(4, dtype=float)

    base_transform_g_b = np.asarray(base_transform_g_b, dtype=float)
    if base_transform_g_b.shape != (4, 4):
        raise ValueError(
            f"base_transform_g_b must have shape (4, 4), got {base_transform_g_b.shape}"
        )

    end_effector_transform_b_e = forward_kinematics(
        joint_angles,
        dh_params=dh_params,
    ).end_effector_transform
    camera_transform_e_c = camera_mount_transform(mount)
    return base_transform_g_b @ end_effector_transform_b_e @ camera_transform_e_c
