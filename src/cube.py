"""Cube point helpers for object projection examples."""

from __future__ import annotations

from typing import Sequence

import numpy as np


DEFAULT_CUBE_CENTER_G: tuple[float, float, float] = (1.40, 0.60, 1.80)
DEFAULT_CUBE_SIDE_LENGTH: float = 0.20


def validate_side_length(side_length: float) -> float:
    """Validate and return a positive cube side length."""

    side_length = float(side_length)
    if side_length <= 0.0:
        raise ValueError(f"side_length must be positive, got {side_length}")
    return side_length


def as_3d_vector(vector: Sequence[float], name: str) -> np.ndarray:
    """Convert a sequence into a 3D vector."""

    vector_array = np.asarray(vector, dtype=float)
    if vector_array.shape != (3,):
        raise ValueError(f"{name} must have shape (3,), got {vector_array.shape}")
    return vector_array


def cube_vertices_local(side_length: float) -> np.ndarray:
    """Return the 8 cube vertices centered at the local origin."""

    half = validate_side_length(side_length) / 2.0
    return np.array(
        [
            [-half, -half, -half],
            [half, -half, -half],
            [half, half, -half],
            [-half, half, -half],
            [-half, -half, half],
            [half, -half, half],
            [half, half, half],
            [-half, half, half],
        ],
        dtype=float,
    )


def cube_vertices_world(center: Sequence[float], side_length: float) -> np.ndarray:
    """Return 8 world-aligned cube vertices for a given center."""

    center_array = as_3d_vector(center, "center")
    return cube_vertices_local(side_length) + center_array


def cube_vertex_world(
    center: Sequence[float],
    side_length: float,
    signs: Sequence[int] = (1, 1, 1),
) -> np.ndarray:
    """Return one cube vertex using signs such as (1, 1, 1)."""

    center_array = as_3d_vector(center, "center")
    signs_array = np.asarray(signs, dtype=float)
    if signs_array.shape != (3,):
        raise ValueError(f"signs must have shape (3,), got {signs_array.shape}")
    if not np.all(np.isin(signs_array, [-1.0, 1.0])):
        raise ValueError("signs must contain only -1 or 1")

    half = validate_side_length(side_length) / 2.0
    return center_array + half * signs_array


# Fixed world-space cube used by phases 5-9.
CUBE_EDGES: list[tuple[int, int]] = [
    (0, 1), (1, 2), (2, 3), (3, 0),   # bottom face
    (4, 5), (5, 6), (6, 7), (7, 4),   # top face
    (0, 4), (1, 5), (2, 6), (3, 7),   # vertical pillars
]
