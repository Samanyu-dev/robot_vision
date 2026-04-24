"""Generate demo GIFs for the Robot Vision Lab README.

Uses Matplotlib (not Plotly/Kaleido) for the 3D GIF to avoid Chrome dependency.

Run with:
    python scripts/generate_gifs.py
"""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import io

import cv2
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

from camera import CameraMount, camera_pose_in_global
from cube import CUBE_EDGES, cube_vertices_world
from kinematics import forward_kinematics
from projection import CameraIntrinsics, project_world_point
from visualization import build_camera_frame_opencv

matplotlib.use("Agg")

DEFAULT_CUBE_CENTER_G = (1.40, 0.60, 1.80)
DEFAULT_CUBE_SIDE_LENGTH = 0.20


def trajectory_angles(t: float) -> np.ndarray:
    return np.deg2rad([
        30.0 + 20.0 * np.sin(t),
        45.0 + 15.0 * np.sin(2.0 * t),
        -20.0 + 10.0 * np.cos(t),
    ])


def _set_equal_3d_axes(ax: plt.Axes, points: np.ndarray) -> None:
    mins = points.min(axis=0)
    maxs = points.max(axis=0)
    center = (mins + maxs) / 2.0
    radius = max(float((maxs - mins).max()) / 2.0, 0.5)
    ax.set_xlim(center[0] - radius, center[0] + radius)
    ax.set_ylim(center[1] - radius, center[1] + radius)
    ax.set_zlim(max(0.0, center[2] - radius), center[2] + radius)


def _draw_frame(ax: plt.Axes, transform: np.ndarray, scale: float, label: str) -> None:
    origin = transform[:3, 3]
    axes = transform[:3, :3]
    colors = ("#ff5252", "#69f0ae", "#40c4ff")
    for axis_index, color in enumerate(colors):
        direction = axes[:, axis_index] * scale
        ax.quiver(
            origin[0], origin[1], origin[2],
            direction[0], direction[1], direction[2],
            color=color, linewidth=2.0, arrow_length_ratio=0.25,
        )
    ax.text(origin[0], origin[1], origin[2], label, color="white", fontsize=10, fontweight="bold")


def build_robot_plot_matplotlib(
    joint_angles: np.ndarray,
    cube_vertices: np.ndarray,
    camera_transform_g_c: np.ndarray,
) -> plt.Figure:
    """Create the 3D robot figure using Matplotlib (no Chrome needed)."""
    fk = forward_kinematics(joint_angles)
    origins = fk.origins
    camera_origin = camera_transform_g_c[:3, 3]
    optical_axis = camera_transform_g_c[:3, 2]

    fig = plt.figure(figsize=(8, 7), facecolor="#0b1017")
    ax = fig.add_subplot(111, projection="3d", facecolor="#0b1017")

    # Ground grid
    ground_x = np.linspace(-0.3, 1.6, 2)
    ground_y = np.linspace(-0.75, 0.75, 2)
    grid_x, grid_y = np.meshgrid(ground_x, ground_y)
    grid_z = np.zeros_like(grid_x)
    ax.plot_surface(grid_x, grid_y, grid_z, color="#18202b", alpha=0.3, linewidth=0)

    # Robot arm
    ax.plot(origins[:, 0], origins[:, 1], origins[:, 2], "-o",
            color="#4fc3f7", linewidth=4, markersize=8,
            markerfacecolor="white", markeredgecolor="#0b1017", markeredgewidth=2)

    # Camera
    ax.scatter([camera_origin[0]], [camera_origin[1]], [camera_origin[2]],
               color="#ff5ad1", s=120, marker="s", depthshade=False,
               edgecolors="white", linewidths=1.5, label="Camera")
    ax.quiver(
        camera_origin[0], camera_origin[1], camera_origin[2],
        optical_axis[0] * 0.25, optical_axis[1] * 0.25, optical_axis[2] * 0.25,
        color="#ff5ad1", linewidth=2.5, arrow_length_ratio=0.3,
    )

    # Cube edges
    for start, end in CUBE_EDGES:
        segment = cube_vertices[[start, end]]
        ax.plot(segment[:, 0], segment[:, 1], segment[:, 2],
                color="#ff6f61", linewidth=2.2)

    # Coordinate frames
    _draw_frame(ax, np.eye(4), scale=0.18, label="G")
    _draw_frame(ax, fk.end_effector_transform, scale=0.14, label="E")
    _draw_frame(ax, camera_transform_g_c, scale=0.12, label="C")

    all_points = np.vstack([origins, cube_vertices, camera_origin.reshape(1, 3)])
    _set_equal_3d_axes(ax, all_points)

    ax.set_xlabel("X [m]", color="white", fontsize=10)
    ax.set_ylabel("Y [m]", color="white", fontsize=10)
    ax.set_zlabel("Z [m]", color="white", fontsize=10)
    ax.set_title("🤖 3R Robot + Wrist Camera + Cube", color="white",
                 fontsize=13, fontweight="bold", pad=15)
    ax.view_init(elev=24, azim=-45)
    ax.tick_params(colors="white")
    for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
        pane.fill = False
        pane.set_edgecolor("#39485b")

    fig.tight_layout()
    return fig


def generate_gif_3d(n_frames: int = 60, fps: int = 15) -> io.BytesIO:
    """Generate 3D robot trajectory GIF using Matplotlib (no Chrome required)."""
    t_total = 2.0 * np.pi
    t_vec = np.linspace(0.0, t_total, n_frames)
    mount = CameraMount(translation_e=(0.08, 0.0, 0.04), tilt_rad=np.deg2rad(-20.0))
    cube_center = np.array(DEFAULT_CUBE_CENTER_G, dtype=float)

    frames: list[Image.Image] = []

    for t_value in t_vec:
        angles = trajectory_angles(t_value)
        cam_t = camera_pose_in_global(angles, mount=mount)
        cube_v = cube_vertices_world(cube_center, DEFAULT_CUBE_SIDE_LENGTH)

        fig = build_robot_plot_matplotlib(angles, cube_v, cam_t)
        fig.suptitle(f"t = {t_value:.2f} s", color="white", fontsize=11, y=0.98)

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=100, facecolor="#0b1017")
        buf.seek(0)
        frames.append(Image.open(buf))
        plt.close(fig)

    gif_buf = io.BytesIO()
    frames[0].save(
        gif_buf,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / fps),
        loop=0,
        optimize=True,
    )
    gif_buf.seek(0)
    return gif_buf


def generate_gif_camera(n_frames: int = 60, fps: int = 15) -> io.BytesIO:
    """Generate camera view trajectory GIF using OpenCV."""
    t_total = 2.0 * np.pi
    t_vec = np.linspace(0.0, t_total, n_frames)
    mount = CameraMount(translation_e=(0.08, 0.0, 0.04), tilt_rad=np.deg2rad(-20.0))
    intrinsics = CameraIntrinsics(fx=600.0, fy=600.0, cx=320.0, cy=240.0)
    cube_center = np.array(DEFAULT_CUBE_CENTER_G, dtype=float)

    frames: list[Image.Image] = []

    for t_value in t_vec:
        angles = trajectory_angles(t_value)
        cam_t = camera_pose_in_global(angles, mount=mount)
        cube_v = cube_vertices_world(cube_center, DEFAULT_CUBE_SIDE_LENGTH)

        projections = [project_world_point(v, cam_t, intrinsics) for v in cube_v]
        pixels = np.array([p.pixel for p in projections])
        mask = np.array([p.in_front and p.in_bounds for p in projections], dtype=bool)

        frame = build_camera_frame_opencv(pixels, mask, intrinsics.width, intrinsics.height, intrinsics.cx, intrinsics.cy)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(Image.fromarray(frame_rgb))

    gif_buf = io.BytesIO()
    frames[0].save(
        gif_buf,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / fps),
        loop=0,
        optimize=True,
    )
    gif_buf.seek(0)
    return gif_buf


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate demo GIFs for Robot Vision Lab")
    parser.add_argument("--output-dir", type=str, default="outputs", help="Output directory for GIFs")
    parser.add_argument("--frames", type=int, default=60, help="Number of frames")
    parser.add_argument("--fps", type=int, default=15, help="Frames per second")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    print("🎥 Generating 3D Robot Trajectory GIF (Matplotlib)...")
    gif_3d = generate_gif_3d(n_frames=args.frames, fps=args.fps)
    path_3d = output_dir / "robot_trajectory_3d.gif"
    with open(path_3d, "wb") as f:
        f.write(gif_3d.getbuffer())
    print(f"   ✅ Saved: {path_3d}")

    print("📷 Generating Camera View GIF (OpenCV)...")
    gif_cam = generate_gif_camera(n_frames=args.frames, fps=args.fps)
    path_cam = output_dir / "camera_view.gif"
    with open(path_cam, "wb") as f:
        f.write(gif_cam.getbuffer())
    print(f"   ✅ Saved: {path_cam}")

    print("\n🎉 Done! Add these GIFs to your README with:")
    print(f'   ![3D Trajectory]({path_3d.relative_to(Path.cwd())})')
    print(f'   ![Camera View]({path_cam.relative_to(Path.cwd())})')
