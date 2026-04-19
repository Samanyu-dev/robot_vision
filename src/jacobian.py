"""Geometric Jacobian for the 3R revolute manipulator."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from kinematics import DEFAULT_DH_PARAMS, DHLink, ForwardKinematicsResult, forward_kinematics


def geometric_jacobian(
    joint_angles: Sequence[float],
    dh_params: Sequence[DHLink] = DEFAULT_DH_PARAMS,
) -> np.ndarray:
    """Return the 6 x 3 geometric Jacobian in the base frame."""

    result: ForwardKinematicsResult = forward_kinematics(joint_angles, dh_params)
    origins = result.origins
    z_axes = result.z_axes
    o_e = origins[-1]

    jacobian = np.zeros((6, 3), dtype=float)
    for index in range(3):
        jacobian[:3, index] = np.cross(z_axes[index], o_e - origins[index])
        jacobian[3:, index] = z_axes[index]
    return jacobian


def joint_velocities_from_end_effector(
    spatial_velocity: Sequence[float],
    joint_angles: Sequence[float],
    dh_params: Sequence[DHLink] = DEFAULT_DH_PARAMS,
) -> np.ndarray:
    """Return minimum-norm q_dot = pinv(J) @ V."""

    velocity = np.asarray(spatial_velocity, dtype=float)
    if velocity.shape != (6,):
        raise ValueError(f"spatial_velocity must have shape (6,), got {velocity.shape}")

    jacobian = geometric_jacobian(joint_angles, dh_params)
    return np.linalg.pinv(jacobian) @ velocity


def manipulability(joint_angles: Sequence[float]) -> float:
    """Return Yoshikawa manipulability sqrt(det(J^T J))."""

    jacobian = geometric_jacobian(joint_angles)
    return float(np.sqrt(max(0.0, np.linalg.det(jacobian.T @ jacobian))))
