"""Phase 8 - Animated 3D robot simulation dashboard.

Outputs
-------
outputs/phase8_simulation_3d.gif
outputs/phase8_snapshot_3d.png
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.gridspec import GridSpec
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

matplotlib.use("Agg")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from camera import CameraMount, camera_pose_in_global  # noqa: E402
from cube import CUBE_EDGES, cube_vertices_world  # noqa: E402
from kinematics import forward_kinematics  # noqa: E402
from projection import CameraIntrinsics  # noqa: E402

N_FRAMES = 80
T_TOTAL = 2.0 * np.pi
T_VEC = np.linspace(0.0, T_TOTAL, N_FRAMES)
MOUNT = CameraMount(translation_e=(0.08, 0.0, 0.04), tilt_rad=np.deg2rad(-20.0))
INTRINSICS = CameraIntrinsics(fx=600.0, fy=600.0, cx=320.0, cy=240.0)
CUBE_SIDE = 0.20
AXIS_LEN = 0.12
FRUSTUM_DEPTH = 0.32


def joint_angles_at(t_value: float) -> np.ndarray:
    """Return the robot trajectory at time t."""

    return np.deg2rad(
        [
            30.0 + 20.0 * np.sin(t_value),
            45.0 + 15.0 * np.sin(2.0 * t_value),
            -20.0 + 10.0 * np.cos(t_value),
        ]
    )


def build_frame_data() -> dict[str, np.ndarray]:
    """Precompute trajectory data used by plots and animation."""

    joint_angles = np.array([joint_angles_at(t_value) for t_value in T_VEC])
    fk_results = [forward_kinematics(angles) for angles in joint_angles]
    camera_transforms = np.array(
        [camera_pose_in_global(angles, mount=MOUNT) for angles in joint_angles]
    )
    cube_centers = np.array(
        [
            (transform @ np.array([0.0, 0.0, 1.20, 1.0], dtype=float))[:3]
            for transform in camera_transforms
        ]
    )
    end_effector_positions = np.array([result.origins[-1] for result in fk_results])
    camera_positions = camera_transforms[:, :3, 3]
    camera_to_cube_distance = np.linalg.norm(cube_centers - camera_positions, axis=1)

    return {
        "joint_angles": joint_angles,
        "joint_angles_deg": np.rad2deg(joint_angles),
        "fk_results": np.array(fk_results, dtype=object),
        "camera_transforms": camera_transforms,
        "cube_centers": cube_centers,
        "end_effector_positions": end_effector_positions,
        "camera_positions": camera_positions,
        "camera_to_cube_distance": camera_to_cube_distance,
    }


FRAME_DATA = build_frame_data()


def draw_frame_axes(ax: Axes3D, transform: np.ndarray, scale: float = AXIS_LEN) -> None:
    """Draw local xyz axes for a homogeneous transform."""

    origin = transform[:3, 3]
    for column, color in zip(range(3), ("#ff5252", "#69f0ae", "#40c4ff")):
        ax.quiver(
            *origin,
            *(transform[:3, column] * scale),
            color=color,
            linewidth=1.2,
            arrow_length_ratio=0.3,
        )


def cube_faces(vertices: np.ndarray) -> list[list[np.ndarray]]:
    """Return face polygons for a cube."""

    return [
        [vertices[0], vertices[1], vertices[2], vertices[3]],
        [vertices[4], vertices[5], vertices[6], vertices[7]],
        [vertices[0], vertices[1], vertices[5], vertices[4]],
        [vertices[2], vertices[3], vertices[7], vertices[6]],
        [vertices[1], vertices[2], vertices[6], vertices[5]],
        [vertices[0], vertices[3], vertices[7], vertices[4]],
    ]


def camera_frustum_world(
    camera_transform: np.ndarray,
    intrinsics: CameraIntrinsics,
    depth: float = FRUSTUM_DEPTH,
) -> tuple[np.ndarray, np.ndarray]:
    """Return world-frame frustum corners and camera origin."""

    corners_uv = np.array(
        [
            [0.0, 0.0],
            [intrinsics.width, 0.0],
            [intrinsics.width, intrinsics.height],
            [0.0, intrinsics.height],
        ],
        dtype=float,
    )

    corners_camera = []
    for u_coord, v_coord in corners_uv:
        x_coord = (u_coord - intrinsics.cx) * depth / intrinsics.fx
        y_coord = (v_coord - intrinsics.cy) * depth / intrinsics.fy
        corners_camera.append([x_coord, y_coord, depth, 1.0])
    corners_camera = np.array(corners_camera, dtype=float)
    corners_world = (camera_transform @ corners_camera.T).T[:, :3]
    return corners_world, camera_transform[:3, 3]


def style_info_axis(axis: plt.Axes, title: str) -> None:
    """Apply the shared dark style to a 2D axes."""

    axis.set_facecolor("#10161f")
    axis.tick_params(colors="white", labelsize=8)
    for spine in axis.spines.values():
        spine.set_edgecolor("#4b5665")
    axis.grid(True, color="#2f3b4c", linewidth=0.6, alpha=0.7)
    axis.set_title(title, color="white", fontsize=10)


def setup_scene_axis(ax: Axes3D, frame_index: int) -> None:
    """Configure the 3D scene axis."""

    ax.set_facecolor("#0f141d")
    ax.set_xlim(-0.3, 1.8)
    ax.set_ylim(-0.8, 0.8)
    ax.set_zlim(0.0, 1.9)
    ax.set_xlabel("X [m]", color="white")
    ax.set_ylabel("Y [m]", color="white")
    ax.set_zlabel("Z [m]", color="white")
    ax.tick_params(colors="white", labelsize=8)
    ax.view_init(elev=23, azim=-57)
    ax.set_title(
        f"Phase 8 - 3D Simulation Dashboard  [t = {T_VEC[frame_index]:.2f} s]",
        color="white",
        fontsize=12,
        pad=12,
    )
    for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
        pane.fill = False
        pane.set_edgecolor("#39485b")


def draw_scene(ax: Axes3D, frame_index: int) -> None:
    """Draw the robot, camera, cube, and motion cues for one frame."""

    result = FRAME_DATA["fk_results"][frame_index]
    t_g_c = FRAME_DATA["camera_transforms"][frame_index]
    cube_center = FRAME_DATA["cube_centers"][frame_index]
    origins = result.origins

    ground_x = np.linspace(-0.3, 1.6, 2)
    ground_y = np.linspace(-0.75, 0.75, 2)
    grid_x, grid_y = np.meshgrid(ground_x, ground_y)
    grid_z = np.zeros_like(grid_x)
    ax.plot_surface(grid_x, grid_y, grid_z, color="#18202b", alpha=0.22, linewidth=0)

    for direction, color in zip(np.eye(3), ("#ff5252", "#69f0ae", "#40c4ff")):
        ax.quiver(0.0, 0.0, 0.0, *(direction * AXIS_LEN * 2.2), color=color, linewidth=2.2)

    for index in range(len(origins) - 1):
        ax.plot(
            [origins[index, 0], origins[index + 1, 0]],
            [origins[index, 1], origins[index + 1, 1]],
            [origins[index, 2], origins[index + 1, 2]],
            color="#4fc3f7",
            linewidth=4,
        )

    for origin in origins:
        ax.scatter(*origin, color="white", s=34, depthshade=False, edgecolors="#0f141d")

    for transform in result.transforms:
        draw_frame_axes(ax, transform)

    camera_origin = t_g_c[:3, 3]
    ax.scatter(*camera_origin, color="#ff5ad1", s=90, marker="s", depthshade=False)
    ax.quiver(
        *camera_origin,
        *(t_g_c[:3, 2] * 0.28),
        color="#ff5ad1",
        linewidth=1.8,
        arrow_length_ratio=0.28,
    )

    frustum_corners, frustum_origin = camera_frustum_world(t_g_c, INTRINSICS)
    for corner in frustum_corners:
        ax.plot(
            [frustum_origin[0], corner[0]],
            [frustum_origin[1], corner[1]],
            [frustum_origin[2], corner[2]],
            color="#ff8be9",
            linewidth=1.0,
            alpha=0.8,
        )
    for index in range(4):
        next_index = (index + 1) % 4
        ax.plot(
            [frustum_corners[index, 0], frustum_corners[next_index, 0]],
            [frustum_corners[index, 1], frustum_corners[next_index, 1]],
            [frustum_corners[index, 2], frustum_corners[next_index, 2]],
            color="#ff8be9",
            linewidth=1.0,
            alpha=0.8,
        )

    vertices = cube_vertices_world(cube_center, CUBE_SIDE)
    cube_mesh = Poly3DCollection(
        cube_faces(vertices),
        facecolors="#ff5252",
        alpha=0.10,
        edgecolors="none",
    )
    ax.add_collection3d(cube_mesh)
    for index0, index1 in CUBE_EDGES:
        ax.plot(
            [vertices[index0, 0], vertices[index1, 0]],
            [vertices[index0, 1], vertices[index1, 1]],
            [vertices[index0, 2], vertices[index1, 2]],
            color="#ff6f61",
            linewidth=1.6,
        )

    trail_points = FRAME_DATA["end_effector_positions"][: frame_index + 1]
    if len(trail_points) >= 2:
        ax.plot(
            trail_points[:, 0],
            trail_points[:, 1],
            trail_points[:, 2],
            color="#ffe082",
            linewidth=1.4,
            linestyle="--",
            alpha=0.9,
        )

    ax.text2D(
        0.02,
        0.96,
        (
            f"EE = {np.array2string(origins[-1], precision=3)} m\n"
            f"Cam = {np.array2string(camera_origin, precision=3)} m\n"
            f"Cube distance = {FRAME_DATA['camera_to_cube_distance'][frame_index]:.3f} m"
        ),
        transform=ax.transAxes,
        color="white",
        fontsize=8,
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#121821", edgecolor="#334155", alpha=0.85),
    )


def draw_joint_plot(axis: plt.Axes, frame_index: int) -> None:
    """Draw joint-angle time histories with a current-frame marker."""

    style_info_axis(axis, "Joint Angles vs Time")
    colors = ("#4fc3f7", "#ffb74d", "#ff5ad1")
    labels = ("theta_1", "theta_2", "theta_3")
    joint_angles_deg = FRAME_DATA["joint_angles_deg"]

    for column, color, label in zip(range(3), colors, labels):
        axis.plot(T_VEC, joint_angles_deg[:, column], color=color, linewidth=1.7, label=label)
        axis.plot(
            T_VEC[frame_index],
            joint_angles_deg[frame_index, column],
            "o",
            color=color,
            markersize=5,
        )

    axis.axvline(T_VEC[frame_index], color="white", linewidth=1.0, linestyle="--", alpha=0.8)
    axis.set_ylabel("Angle [deg]", color="white")
    axis.legend(facecolor="#1b2532", edgecolor="#405063", labelcolor="white", fontsize=8)


def draw_position_plot(axis: plt.Axes, frame_index: int) -> None:
    """Draw end-effector coordinates and camera-to-cube distance."""

    style_info_axis(axis, "Workspace Metrics")
    positions = FRAME_DATA["end_effector_positions"]
    colors = ("#69f0ae", "#40c4ff", "#ff8a80")
    labels = ("EE X", "EE Y", "EE Z")

    for column, color, label in zip(range(3), colors, labels):
        axis.plot(T_VEC, positions[:, column], color=color, linewidth=1.5, label=label)
        axis.plot(T_VEC[frame_index], positions[frame_index, column], "o", color=color, markersize=5)

    distance = FRAME_DATA["camera_to_cube_distance"]
    axis.plot(T_VEC, distance, color="#ffe082", linewidth=1.5, linestyle="--", label="Camera-cube")
    axis.plot(T_VEC[frame_index], distance[frame_index], "o", color="#ffe082", markersize=5)

    axis.axvline(T_VEC[frame_index], color="white", linewidth=1.0, linestyle="--", alpha=0.8)
    axis.set_xlabel("t [s]", color="white")
    axis.set_ylabel("Position / Distance [m]", color="white")
    axis.legend(facecolor="#1b2532", edgecolor="#405063", labelcolor="white", fontsize=8)


def render_dashboard(frame_index: int) -> plt.Figure:
    """Create a dashboard-style figure for the given frame."""

    fig = plt.figure(figsize=(13.5, 7.8), facecolor="#0b1017")
    grid = GridSpec(2, 2, figure=fig, width_ratios=(1.75, 1.0), hspace=0.22, wspace=0.16)

    ax_scene = fig.add_subplot(grid[:, 0], projection="3d")
    ax_joints = fig.add_subplot(grid[0, 1])
    ax_metrics = fig.add_subplot(grid[1, 1])

    setup_scene_axis(ax_scene, frame_index)
    draw_scene(ax_scene, frame_index)
    draw_joint_plot(ax_joints, frame_index)
    draw_position_plot(ax_metrics, frame_index)

    fig.subplots_adjust(left=0.03, right=0.98, top=0.94, bottom=0.08)
    return fig


def main() -> None:
    output_dir = PROJECT_ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)

    dashboard_fig = render_dashboard(0)
    axes = dashboard_fig.axes
    scene_ax = axes[0]
    joints_ax = axes[1]
    metrics_ax = axes[2]

    def update(frame_index: int) -> None:
        scene_ax.cla()
        joints_ax.cla()
        metrics_ax.cla()
        setup_scene_axis(scene_ax, frame_index)
        draw_scene(scene_ax, frame_index)
        draw_joint_plot(joints_ax, frame_index)
        draw_position_plot(metrics_ax, frame_index)

    animation = FuncAnimation(
        dashboard_fig,
        update,
        frames=N_FRAMES,
        interval=80,
        repeat=False,
    )
    animation.save(
        str(output_dir / "phase8_simulation_3d.gif"),
        writer=PillowWriter(fps=12),
    )
    plt.close(dashboard_fig)
    print("Saved: outputs/phase8_simulation_3d.gif")

    snapshot_fig = render_dashboard(0)
    snapshot_fig.savefig(
        str(output_dir / "phase8_snapshot_3d.png"),
        dpi=150,
        facecolor=snapshot_fig.get_facecolor(),
    )
    plt.close(snapshot_fig)
    print("Saved: outputs/phase8_snapshot_3d.png")


if __name__ == "__main__":
    main()
