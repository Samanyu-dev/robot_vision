"""Forward kinematics for the 3R robot arm."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np


@dataclass(frozen=True)
class DHLink:
    """Standard DH parameters for one revolute link."""

    d: float
    a: float
    alpha: float
    theta_offset: float = 0.0


@dataclass(frozen=True)
class ForwardKinematicsResult:
    """Frame transforms and geometric data from base to end-effector."""

    joint_angles: np.ndarray
    transforms: tuple[np.ndarray, ...]

    @property
    def end_effector_transform(self) -> np.ndarray:
        """Return T_BE."""

        return self.transforms[-1]

    @property
    def origins(self) -> np.ndarray:
        """Return frame origins o_0 through o_3 in base coordinates."""

        return np.array([transform[:3, 3] for transform in self.transforms])

    @property
    def z_axes(self) -> np.ndarray:
        """Return frame z axes z_0 through z_3 in base coordinates."""

        return np.array([transform[:3, 2] for transform in self.transforms])


DEFAULT_DH_PARAMS: tuple[DHLink, ...] = (
    DHLink(d=0.35, a=0.0, alpha=np.pi / 2.0),
    DHLink(d=0.0, a=0.45, alpha=0.0),
    DHLink(d=0.0, a=0.30, alpha=0.0),
)


def as_joint_array(joint_angles: Iterable[float]) -> np.ndarray:
    """Convert a joint angle iterable to a 3-vector in radians."""

    angles = np.asarray(tuple(joint_angles), dtype=float)
    if angles.shape != (3,):
        raise ValueError(f"expected exactly 3 joint angles, got shape {angles.shape}")
    return angles


def dh_transform(theta: float, d: float, a: float, alpha: float) -> np.ndarray:
    """Build the standard DH transform from frame i-1 to frame i."""

    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    cos_alpha = np.cos(alpha)
    sin_alpha = np.sin(alpha)

    return np.array(
        [
            [cos_theta, -sin_theta * cos_alpha, sin_theta * sin_alpha, a * cos_theta],
            [sin_theta, cos_theta * cos_alpha, -cos_theta * sin_alpha, a * sin_theta],
            [0.0, sin_alpha, cos_alpha, d],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


def forward_kinematics(
    joint_angles: Sequence[float],
    dh_params: Sequence[DHLink] = DEFAULT_DH_PARAMS,
) -> ForwardKinematicsResult:
    """Compute transforms from base frame to each robot frame.

    The returned transform tuple contains:

    - T_B0, the identity transform
    - T_B1
    - T_B2
    - T_B3, also called T_BE in this project
    """

    angles = as_joint_array(joint_angles)
    if len(dh_params) != 3:
        raise ValueError(f"expected 3 DH links, got {len(dh_params)}")

    transforms = [np.eye(4, dtype=float)]
    current = np.eye(4, dtype=float)

    for angle, link in zip(angles, dh_params):
        link_transform = dh_transform(
            theta=angle + link.theta_offset,
            d=link.d,
            a=link.a,
            alpha=link.alpha,
        )
        current = current @ link_transform
        transforms.append(current.copy())

    return ForwardKinematicsResult(
        joint_angles=angles,
        transforms=tuple(transforms),
    )


def end_effector_position(
    joint_angles: Sequence[float],
    dh_params: Sequence[DHLink] = DEFAULT_DH_PARAMS,
) -> np.ndarray:
    """Return only the end-effector position in base coordinates."""

    return forward_kinematics(joint_angles, dh_params).end_effector_transform[:3, 3]

