"""Interactive Streamlit demo for the robot vision project."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from camera import CameraMount, camera_pose_in_global  # noqa: E402
from cube import CUBE_EDGES, cube_vertices_world  # noqa: E402
from kinematics import forward_kinematics  # noqa: E402
from projection import CameraIntrinsics, project_world_point  # noqa: E402


DEFAULT_CUBE_CENTER_G = (1.40, 0.60, 1.80)
DEFAULT_CUBE_SIDE_LENGTH = 0.20


def set_equal_3d_axes(ax: plt.Axes, points: np.ndarray) -> None:
    """Set roughly equal 3D axes around a point cloud."""

    mins = points.min(axis=0)
    maxs = points.max(axis=0)
    center = (mins + maxs) / 2.0
    radius = max(float((maxs - mins).max()) / 2.0, 0.5)

    ax.set_xlim(center[0] - radius, center[0] + radius)
    ax.set_ylim(center[1] - radius, center[1] + radius)
    ax.set_zlim(max(0.0, center[2] - radius), center[2] + radius)


def draw_frame(ax: plt.Axes, transform: np.ndarray, scale: float, label: str) -> None:
    """Draw a small RGB coordinate frame."""

    origin = transform[:3, 3]
    axes = transform[:3, :3]
    colors = ("red", "green", "blue")
    for axis_index, color in enumerate(colors):
        direction = axes[:, axis_index] * scale
        ax.quiver(
            origin[0],
            origin[1],
            origin[2],
            direction[0],
            direction[1],
            direction[2],
            color=color,
            linewidth=1.5,
        )
    ax.text(origin[0], origin[1], origin[2], label)


def build_robot_plot(
    joint_angles: np.ndarray,
    cube_vertices: np.ndarray,
    camera_transform_g_c: np.ndarray,
) -> plt.Figure:
    """Create the 3D robot, camera, and cube figure."""

    fk = forward_kinematics(joint_angles)
    origins = fk.origins
    camera_origin = camera_transform_g_c[:3, 3]
    optical_axis = camera_transform_g_c[:3, 2]

    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, projection="3d")

    ax.plot(origins[:, 0], origins[:, 1], origins[:, 2], "-o", color="black", linewidth=3)
    ax.scatter(
        [camera_origin[0]],
        [camera_origin[1]],
        [camera_origin[2]],
        color="magenta",
        s=70,
        label="Camera",
    )
    ax.quiver(
        camera_origin[0],
        camera_origin[1],
        camera_origin[2],
        optical_axis[0] * 0.25,
        optical_axis[1] * 0.25,
        optical_axis[2] * 0.25,
        color="magenta",
        linewidth=2,
    )

    for start, end in CUBE_EDGES:
        segment = cube_vertices[[start, end]]
        ax.plot(segment[:, 0], segment[:, 1], segment[:, 2], color="red", linewidth=1.8)

    draw_frame(ax, np.eye(4), scale=0.18, label="G/B")
    draw_frame(ax, fk.end_effector_transform, scale=0.14, label="E")
    draw_frame(ax, camera_transform_g_c, scale=0.12, label="C")

    all_points = np.vstack([origins, cube_vertices, camera_origin.reshape(1, 3)])
    set_equal_3d_axes(ax, all_points)
    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    ax.set_zlabel("Z [m]")
    ax.set_title("3R Robot, Wrist Camera, and Cube")
    ax.view_init(elev=24, azim=-45)
    fig.tight_layout()
    return fig


def build_image_plot(
    projected_pixels: np.ndarray,
    visibility_mask: np.ndarray,
    intrinsics: CameraIntrinsics,
) -> plt.Figure:
    """Create the 640 x 480 camera image-plane figure."""

    fig, ax = plt.subplots(figsize=(7, 5.25))
    ax.set_xlim(0, intrinsics.width)
    ax.set_ylim(intrinsics.height, 0)
    ax.set_aspect("equal")
    ax.set_facecolor("#f7f7f7")
    ax.axvline(intrinsics.cx, color="gray", linestyle="--", linewidth=1)
    ax.axhline(intrinsics.cy, color="gray", linestyle="--", linewidth=1)

    for start, end in CUBE_EDGES:
        if visibility_mask[start] and visibility_mask[end]:
            segment = projected_pixels[[start, end]]
            ax.plot(segment[:, 0], segment[:, 1], color="blue", linewidth=2)

    visible_pixels = projected_pixels[visibility_mask]
    if len(visible_pixels) > 0:
        ax.scatter(visible_pixels[:, 0], visible_pixels[:, 1], color="blue", s=35)

    ax.scatter([intrinsics.cx], [intrinsics.cy], color="black", s=30, marker="+")
    ax.set_xlabel("u [px]")
    ax.set_ylabel("v [px]")
    ax.set_title("Camera Image Plane")
    fig.tight_layout()
    return fig


def main() -> None:
    """Render the Streamlit app."""

    st.set_page_config(page_title="Robot Vision Demo", layout="wide")
    st.title("Robot Vision: 3R Arm with Wrist Camera")

    with st.sidebar:
        st.header("Robot")
        theta_1 = st.slider("theta_1 [deg]", -180.0, 180.0, 30.0, 1.0)
        theta_2 = st.slider("theta_2 [deg]", -120.0, 120.0, 45.0, 1.0)
        theta_3 = st.slider("theta_3 [deg]", -120.0, 120.0, -20.0, 1.0)

        st.header("Cube")
        cube_side = st.slider("side length [m]", 0.05, 0.60, DEFAULT_CUBE_SIDE_LENGTH, 0.01)
        cube_x = st.number_input("cube center X [m]", value=DEFAULT_CUBE_CENTER_G[0], step=0.05)
        cube_y = st.number_input("cube center Y [m]", value=DEFAULT_CUBE_CENTER_G[1], step=0.05)
        cube_z = st.number_input("cube center Z [m]", value=DEFAULT_CUBE_CENTER_G[2], step=0.05)

        st.header("Camera")
        focal_length = st.slider("focal length [px]", 250.0, 1000.0, 600.0, 25.0)
        camera_tilt = st.slider("camera tilt [deg]", -60.0, 30.0, -20.0, 1.0)

    joint_angles = np.deg2rad([theta_1, theta_2, theta_3])
    mount = CameraMount(translation_e=(0.08, 0.0, 0.04), tilt_rad=np.deg2rad(camera_tilt))
    intrinsics = CameraIntrinsics(fx=focal_length, fy=focal_length, cx=320.0, cy=240.0)
    cube_center = np.array([cube_x, cube_y, cube_z], dtype=float)

    camera_transform_g_c = camera_pose_in_global(joint_angles, mount=mount)
    cube_vertices = cube_vertices_world(cube_center, cube_side)
    projections = [project_world_point(vertex, camera_transform_g_c, intrinsics) for vertex in cube_vertices]
    projected_pixels = np.array([projection.pixel for projection in projections])
    visibility_mask = np.array(
        [projection.in_front and projection.in_bounds for projection in projections],
        dtype=bool,
    )

    status_col, camera_col, visible_col = st.columns(3)
    status_col.metric("Visible vertices", f"{int(visibility_mask.sum())} / 8")
    camera_col.metric("Camera Z [m]", f"{camera_transform_g_c[2, 3]:.3f}")
    visible_col.metric("Image status", "IN VIEW" if visibility_mask.all() else "OUT OF VIEW")

    left, right = st.columns(2)
    with left:
        st.pyplot(build_robot_plot(joint_angles, cube_vertices, camera_transform_g_c))
    with right:
        st.pyplot(build_image_plot(projected_pixels, visibility_mask, intrinsics))

    with st.expander("Current matrices"):
        st.write("T_GC")
        st.code(np.array2string(camera_transform_g_c, precision=5, suppress_small=True))
        st.write("Projected pixels")
        st.code(np.array2string(projected_pixels, precision=3, suppress_small=True))


if __name__ == "__main__":
    main()
