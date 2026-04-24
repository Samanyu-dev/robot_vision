"""Premium Robot Vision Lab — Interactive 3R Manipulator Dashboard.

Features:
- Interactive Plotly 3D robot scene with rotation/zoom/pan
- OpenCV-based simulated camera view with projection overlay
- Real-time joint angle sliders + trajectory animation
- Live metrics dashboard, Jacobian analytics, and matrix lab
- Premium dark futuristic UI with glassmorphism, particles, and animations
"""

from __future__ import annotations

import io
import sys
import time
from pathlib import Path
from typing import Sequence

import cv2
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

matplotlib.use("Agg")

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from camera import CameraMount, camera_pose_in_global  # noqa: E402
from cube import CUBE_EDGES, cube_vertices_world  # noqa: E402
from jacobian import geometric_jacobian, manipulability  # noqa: E402
from kinematics import forward_kinematics  # noqa: E402
from projection import CameraIntrinsics, project_world_point  # noqa: E402
from ui_components import footer, hero_header, inject_premium_css, metric_card_html  # noqa: E402
from visualization import (  # noqa: E402
    build_camera_frame_opencv,
    build_robot_plotly,
    build_trajectory_plotly,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_CUBE_CENTER_G = (1.40, 0.60, 1.80)
DEFAULT_CUBE_SIDE_LENGTH = 0.20

# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------


def init_session_state() -> None:
    """Initialize Streamlit session state for animation and trajectory."""
    defaults = {
        "animation_running": False,
        "animation_time": 0.0,
        "animation_speed": 1.0,
        "uv_history": [],
        "auto_mode": False,
        "theta_history": [],
        "frame_count": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_trajectory() -> None:
    """Clear trajectory history."""
    st.session_state.uv_history = []
    st.session_state.theta_history = []
    st.session_state.frame_count = 0


# ---------------------------------------------------------------------------
# Core computation
# ---------------------------------------------------------------------------


def compute_scene(
    theta_1_deg: float,
    theta_2_deg: float,
    theta_3_deg: float,
    cube_side: float,
    cube_x: float,
    cube_y: float,
    cube_z: float,
    focal_length: float,
    camera_tilt_deg: float,
) -> dict:
    """Compute full kinematics, projection, and analytics for the scene."""
    joint_angles = np.deg2rad([theta_1_deg, theta_2_deg, theta_3_deg])
    mount = CameraMount(translation_e=(0.08, 0.0, 0.04), tilt_rad=np.deg2rad(camera_tilt_deg))
    intrinsics = CameraIntrinsics(fx=focal_length, fy=focal_length, cx=320.0, cy=240.0)
    cube_center = np.array([cube_x, cube_y, cube_z], dtype=float)

    fk = forward_kinematics(joint_angles)
    camera_transform_g_c = camera_pose_in_global(joint_angles, mount=mount)
    cube_vertices = cube_vertices_world(cube_center, cube_side)

    projections = [project_world_point(vertex, camera_transform_g_c, intrinsics) for vertex in cube_vertices]
    projected_pixels = np.array([p.pixel for p in projections])
    visibility_mask = np.array([p.in_front and p.in_bounds for p in projections], dtype=bool)

    jacobian = geometric_jacobian(joint_angles)
    manip = manipulability(joint_angles)
    ee_pos = fk.end_effector_transform[:3, 3]
    cam_pos = camera_transform_g_c[:3, 3]

    # Trajectory tracking — centroid of visible projected pixels
    visible_pixels = projected_pixels[visibility_mask]
    if len(visible_pixels) > 0:
        centroid = (float(visible_pixels[:, 0].mean()), float(visible_pixels[:, 1].mean()))
    else:
        centroid = (np.nan, np.nan)

    return {
        "joint_angles": joint_angles,
        "fk": fk,
        "camera_transform_g_c": camera_transform_g_c,
        "cube_vertices": cube_vertices,
        "projected_pixels": projected_pixels,
        "visibility_mask": visibility_mask,
        "intrinsics": intrinsics,
        "jacobian": jacobian,
        "manipulability": manip,
        "ee_pos": ee_pos,
        "cam_pos": cam_pos,
        "cube_center": cube_center,
        "centroid": centroid,
    }


# ---------------------------------------------------------------------------
# Animation helpers
# ---------------------------------------------------------------------------


def trajectory_angles(t: float) -> np.ndarray:
    """Return joint angles for the pre-defined trajectory at time t."""
    return np.deg2rad([
        30.0 + 20.0 * np.sin(t),
        45.0 + 15.0 * np.sin(2.0 * t),
        -20.0 + 10.0 * np.cos(t),
    ])


def generate_gif_3d(n_frames: int = 60, fps: int = 15) -> io.BytesIO:
    """Generate an animated GIF of the 3D robot trajectory."""
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

        fig = build_robot_plotly(
            forward_kinematics(angles), cube_v, cam_t, show_frames=True, wireframe_cube=False
        )
        fig.update_layout(title=dict(text=f"t = {t_value:.2f} s", font=dict(size=14)))

        img_bytes = fig.to_image(format="png", width=800, height=650, scale=1)
        frames.append(Image.open(io.BytesIO(img_bytes)))

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
    """Generate an animated GIF of the camera view trajectory."""
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


# ---------------------------------------------------------------------------
# Matplotlib fallback for Jacobian heatmap
# ---------------------------------------------------------------------------


def build_jacobian_plot(joint_angles: np.ndarray, dark: bool = True) -> plt.Figure:
    """Visualize the geometric Jacobian as a heatmap."""
    jacobian = geometric_jacobian(joint_angles)
    fig, ax = plt.subplots(figsize=(7, 4), facecolor="#0b1017" if dark else "white")
    ax.set_facecolor("#0b1017" if dark else "white")

    im = ax.imshow(jacobian, cmap="plasma", aspect="auto", vmin=-1.5, vmax=1.5)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["θ₁", "θ₂", "θ₃"], color="white" if dark else "black", fontsize=12)
    ax.set_yticks([0, 1, 2, 3, 4, 5])
    ax.set_yticklabels(["vₓ", "vᵧ", "v₂", "ωₓ", "ωᵧ", "ω₂"],
                       color="white" if dark else "black", fontsize=11)
    ax.set_title("🔥 Geometric Jacobian J(q)", color="white" if dark else "black",
                 fontsize=13, fontweight="bold", pad=10)

    for i in range(6):
        for j in range(3):
            text_color = "white" if abs(jacobian[i, j]) > 0.75 else "black"
            ax.text(j, i, f"{jacobian[i, j]:.2f}", ha="center", va="center",
                    color=text_color, fontsize=9, fontweight="bold")

    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Value", color="white" if dark else "black", fontsize=10)
    if dark:
        cbar.ax.yaxis.set_tick_params(color="white")
        plt.setp(cbar.ax.yaxis.get_ticklabels(), color="white")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_edgecolor("#2f3b4c")

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------


def main() -> None:
    """Render the premium Robot Vision Lab dashboard."""
    st.set_page_config(
        page_title="🤖 Robot Vision Lab",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()
    inject_premium_css()
    hero_header()

    # ── Sidebar controls ──────────────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="sidebar-title">⚙️ Robot Controls</div>', unsafe_allow_html=True)

        auto_mode = st.toggle(
            "🎬 Auto Trajectory",
            value=st.session_state.auto_mode,
            help="Toggle automatic sinusoidal trajectory animation",
        )
        st.session_state.auto_mode = auto_mode

        if auto_mode:
            speed = st.slider("animation speed", 0.1, 3.0, st.session_state.animation_speed, 0.1,
                              help="Multiplier for animation speed")
            st.session_state.animation_speed = speed

            c_play, c_stop = st.columns(2)
            with c_play:
                if st.button("▶ PLAY", use_container_width=True, key="play_btn"):
                    st.session_state.animation_running = True
            with c_stop:
                if st.button("⏹ STOP", use_container_width=True, key="stop_btn"):
                    st.session_state.animation_running = False

            if st.session_state.animation_running:
                st.session_state.animation_time += 0.05 * speed
                time.sleep(0.03)
                st.rerun()
        else:
            st.session_state.animation_running = False

        # Manual sliders
        if auto_mode and st.session_state.animation_running:
            t = st.session_state.animation_time
            theta_1 = float(np.rad2deg(trajectory_angles(t)[0]))
            theta_2 = float(np.rad2deg(trajectory_angles(t)[1]))
            theta_3 = float(np.rad2deg(trajectory_angles(t)[2]))
            st.markdown(
                f"<div style='color:#4fc3f7;font-family:Orbitron;font-size:0.8rem;'>"
                f"t = {t:.2f} s</div>",
                unsafe_allow_html=True,
            )
        else:
            theta_1 = st.slider("θ₁ [deg]", -180.0, 180.0, 30.0, 1.0, help="Base joint rotation")
            theta_2 = st.slider("θ₂ [deg]", -120.0, 120.0, 45.0, 1.0, help="Shoulder joint rotation")
            theta_3 = st.slider("θ₃ [deg]", -120.0, 120.0, -20.0, 1.0, help="Wrist joint rotation")

        st.markdown('<div class="sidebar-title">📦 Cube Controls</div>', unsafe_allow_html=True)
        cube_side = st.slider("side length [m]", 0.05, 0.60, DEFAULT_CUBE_SIDE_LENGTH, 0.01)
        cube_x = st.number_input("center X [m]", value=DEFAULT_CUBE_CENTER_G[0], step=0.05, format="%.2f")
        cube_y = st.number_input("center Y [m]", value=DEFAULT_CUBE_CENTER_G[1], step=0.05, format="%.2f")
        cube_z = st.number_input("center Z [m]", value=DEFAULT_CUBE_CENTER_G[2], step=0.05, format="%.2f")

        st.markdown('<div class="sidebar-title">📷 Camera Controls</div>', unsafe_allow_html=True)
        focal_length = st.slider("focal length [px]", 250.0, 1000.0, 600.0, 25.0)
        camera_tilt = st.slider("camera tilt [deg]", -60.0, 30.0, -20.0, 1.0)

        st.markdown('<div class="sidebar-title">🎨 View Options</div>', unsafe_allow_html=True)
        show_frames = st.checkbox("Show coordinate frames", value=True)
        wireframe_cube = st.checkbox("Wireframe cube only", value=False)
        show_camera_grid = st.checkbox("Show camera grid", value=True)

        st.markdown("---")
        if st.button("🔄 Reset Trajectory", use_container_width=True):
            reset_trajectory()
            st.rerun()

        st.markdown(
            "<div style='text-align:center; color:#4fc3f7; font-family:Orbitron; font-size:0.7rem;'>"
            "Premium v3.0</div>",
            unsafe_allow_html=True,
        )

    # ── Compute scene ─────────────────────────────────────────────────────
    scene = compute_scene(
        theta_1, theta_2, theta_3,
        cube_side, cube_x, cube_y, cube_z,
        focal_length, camera_tilt,
    )

    # Track trajectory
    if not np.isnan(scene["centroid"][0]):
        st.session_state.uv_history.append(scene["centroid"])
        st.session_state.theta_history.append(np.rad2deg(scene["joint_angles"]).tolist())
        st.session_state.frame_count += 1

    # Limit history
    if len(st.session_state.uv_history) > 300:
        st.session_state.uv_history = st.session_state.uv_history[-300:]
        st.session_state.theta_history = st.session_state.theta_history[-300:]

    # ── Metrics dashboard ─────────────────────────────────────────────────
    st.markdown("---")
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(
            metric_card_html("Visible Vertices", f"{int(scene['visibility_mask'].sum())}/8", "#4fc3f7"),
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            metric_card_html("Camera Z [m]", f"{scene['cam_pos'][2]:.3f}", "#ff5ad1"),
            unsafe_allow_html=True,
        )
    with m3:
        status_color = "#69f0ae" if scene["visibility_mask"].all() else "#ff5252"
        status_text = "✅ IN VIEW" if scene["visibility_mask"].all() else "⚠️ OUT OF VIEW"
        st.markdown(
            metric_card_html("Image Status", status_text, status_color),
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            metric_card_html("Manipulability", f"{scene['manipulability']:.3f}", "#ffe082"),
            unsafe_allow_html=True,
        )
    with m5:
        dist = np.linalg.norm(scene["ee_pos"] - scene["cube_center"])
        st.markdown(
            metric_card_html("EE→Cube [m]", f"{dist:.3f}", "#40c4ff"),
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Main tabs ─────────────────────────────────────────────────────────
    tabs = st.tabs([
        "🎮 Live 3D Scene",
        "📷 Camera View",
        "📊 Analytics",
        "🔥 Jacobian",
        "🎬 Trajectory GIFs",
        "🧮 Matrix Lab",
    ])

    # ── Tab 1: Live 3D Scene ──────────────────────────────────────────────
    with tabs[0]:
        c1, c2 = st.columns([3, 1])
        with c1:
            fig_3d = build_robot_plotly(
                scene["fk"],
                scene["cube_vertices"],
                scene["camera_transform_g_c"],
                show_frames=show_frames,
                wireframe_cube=wireframe_cube,
            )
            st.plotly_chart(fig_3d, use_container_width=True, config={"displayModeBar": True})

        with c2:
            st.markdown("#### 📐 End-Effector Pose")
            st.code(
                np.array2string(scene["fk"].end_effector_transform, precision=4, suppress_small=True),
                language="text",
            )

            st.markdown("#### 🎥 Camera Pose (T_GC)")
            st.code(
                np.array2string(scene["camera_transform_g_c"], precision=4, suppress_small=True),
                language="text",
            )

            st.markdown("#### 🔧 Joint Angles")
            st.json({
                "θ₁ [deg]": round(float(np.rad2deg(scene["joint_angles"][0])), 2),
                "θ₂ [deg]": round(float(np.rad2deg(scene["joint_angles"][1])), 2),
                "θ₃ [deg]": round(float(np.rad2deg(scene["joint_angles"][2])), 2),
            })

            st.markdown("#### 📊 Joint Limit Utilization")
            limits = [180.0, 120.0, 120.0]
            names = ["θ₁", "θ₂", "θ₃"]
            colors = ["#4fc3f7", "#ff5ad1", "#ffe082"]
            for i, (name, limit, color) in enumerate(zip(names, limits, colors)):
                deg = abs(float(np.rad2deg(scene["joint_angles"][i])))
                pct = min(deg / limit * 100, 100)
                st.markdown(
                    f"<span style='color:{color};font-family:Orbitron;font-size:0.8rem;'>"
                    f"{name}: {deg:.1f}° / {limit}°</span>",
                    unsafe_allow_html=True,
                )
                st.progress(int(pct))

    # ── Tab 2: Camera View ────────────────────────────────────────────────
    with tabs[1]:
        c1, c2 = st.columns([3, 1])
        with c1:
            frame = build_camera_frame_opencv(
                scene["projected_pixels"],
                scene["visibility_mask"],
                scene["intrinsics"].width,
                scene["intrinsics"].height,
                scene["intrinsics"].cx,
                scene["intrinsics"].cy,
                show_grid=show_camera_grid,
            )
            st.image(frame, channels="BGR", use_container_width=True)

        with c2:
            st.markdown("#### 🎯 Projected Pixels")
            pixel_df = pd.DataFrame({
                "Vertex": list(range(8)),
                "u [px]": [f"{p[0]:.1f}" if not np.isnan(p[0]) else "—" for p in scene["projected_pixels"]],
                "v [px]": [f"{p[1]:.1f}" if not np.isnan(p[1]) else "—" for p in scene["projected_pixels"]],
                "Visible": ["✅" if v else "❌" for v in scene["visibility_mask"]],
            })
            st.dataframe(pixel_df, use_container_width=True, hide_index=True)

            st.markdown("#### 📏 Intrinsics Matrix K")
            k = np.array([
                [scene["intrinsics"].fx, 0, scene["intrinsics"].cx],
                [0, scene["intrinsics"].fy, scene["intrinsics"].cy],
                [0, 0, 1],
            ])
            st.code(np.array2string(k, precision=2, suppress_small=True), language="text")

    # ── Tab 3: Analytics ──────────────────────────────────────────────────
    with tabs[2]:
        ac1, ac2 = st.columns(2)
        with ac1:
            st.markdown("#### 📈 (u, v) Trajectory")
            if len(st.session_state.uv_history) > 1:
                fig_traj = build_trajectory_plotly(
                    st.session_state.uv_history,
                    scene["intrinsics"].width,
                    scene["intrinsics"].height,
                )
                st.plotly_chart(fig_traj, use_container_width=True)
            else:
                st.info("Move the robot to start tracking the projection trajectory.")

        with ac2:
            st.markdown("#### 📊 Position Metrics")
            pos_data = pd.DataFrame({
                "Coordinate": ["X", "Y", "Z"],
                "End-Effector [m]": [f"{scene['ee_pos'][i]:.4f}" for i in range(3)],
                "Camera [m]": [f"{scene['cam_pos'][i]:.4f}" for i in range(3)],
            })
            st.dataframe(pos_data, use_container_width=True, hide_index=True)

            st.markdown("#### 📐 Distance Metrics")
            d1, d2, d3 = st.columns(3)
            with d1:
                st.metric("Base → EE", f"{np.linalg.norm(scene['ee_pos']):.3f} m")
            with d2:
                st.metric("Base → Cam", f"{np.linalg.norm(scene['cam_pos']):.3f} m")
            with d3:
                st.metric("Cam → Cube", f"{np.linalg.norm(scene['cam_pos'] - scene['cube_center']):.3f} m")

        st.markdown("---")
        st.markdown("#### 🧊 Cube Vertices (World Frame)")
        vert_data = pd.DataFrame({
            "Vertex": list(range(8)),
            "X [m]": [f"{v[0]:.3f}" for v in scene["cube_vertices"]],
            "Y [m]": [f"{v[1]:.3f}" for v in scene["cube_vertices"]],
            "Z [m]": [f"{v[2]:.3f}" for v in scene["cube_vertices"]],
        })
        st.dataframe(vert_data, use_container_width=True, hide_index=True)

    # ── Tab 4: Jacobian ───────────────────────────────────────────────────
    with tabs[3]:
        c1, c2 = st.columns([2, 1])
        with c1:
            fig_jac = build_jacobian_plot(scene["joint_angles"], dark=True)
            st.pyplot(fig_jac, use_container_width=True)
            plt.close(fig_jac)

        with c2:
            st.markdown("#### 🧬 Jacobian Matrix J(q)")
            st.code(np.array2string(scene["jacobian"], precision=4, suppress_small=True), language="text")

            st.markdown("#### 📈 Singular Values")
            s = np.linalg.svd(scene["jacobian"], compute_uv=False)
            st.bar_chart({f"σ{i+1}": float(v) for i, v in enumerate(s)})

            st.markdown("#### 💪 Manipulability")
            st.markdown(
                f"<div style='text-align:center;'>"
                f"<span style='font-family:Orbitron;font-size:3rem;color:#ffe082;'>"
                f"{scene['manipulability']:.4f}</span></div>",
                unsafe_allow_html=True,
            )
            st.progress(min(int(scene["manipulability"] / 0.5 * 100), 100))

    # ── Tab 5: Trajectory GIFs ────────────────────────────────────────────
    with tabs[4]:
        st.markdown("#### 🎬 Pre-generated Trajectory Animations")
        st.info("Click the buttons below to generate animated GIFs showing the robot in motion!")

        gc1, gc2 = st.columns(2)
        with gc1:
            if st.button("🎥 Generate 3D Trajectory GIF", use_container_width=True, key="gif3d"):
                with st.spinner("Rendering 60 frames of 3D animation..."):
                    try:
                        gif_3d = generate_gif_3d(n_frames=60, fps=15)
                        st.success("Done!")
                        st.image(gif_3d, use_container_width=True, caption="3D Robot Trajectory Animation")
                    except Exception as e:
                        st.error(f"Plotly image export requires kaleido: pip install kaleido. Error: {e}")

        with gc2:
            if st.button("📷 Generate Camera View GIF", use_container_width=True, key="gifcam"):
                with st.spinner("Rendering 60 frames of camera animation..."):
                    gif_cam = generate_gif_camera(n_frames=60, fps=15)
                    st.success("Done!")
                    st.image(gif_cam, use_container_width=True, caption="Camera View Animation")

        st.markdown("---")
        st.markdown(
            "<div style='text-align:center;color:#64748b;font-size:0.9rem;'>"
            "The trajectory follows:<br>"
            "<code style='color:#4fc3f7;'>θ₁(t) = 30 + 20·sin(t)</code> &nbsp;|&nbsp; "
            "<code style='color:#ff5ad1;'>θ₂(t) = 45 + 15·sin(2t)</code> &nbsp;|&nbsp; "
            "<code style='color:#ffe082;'>θ₃(t) = -20 + 10·cos(t)</code>"
            "</div>",
            unsafe_allow_html=True,
        )

    # ── Tab 6: Matrix Lab ─────────────────────────────────────────────────
    with tabs[5]:
        st.markdown("#### 🧮 Homogeneous Transformation Matrices")

        mc1, mc2 = st.columns(2)
        with mc1:
            st.markdown("**T_BE — Base → End-Effector**")
            st.code(
                np.array2string(scene["fk"].end_effector_transform, precision=6, suppress_small=True),
                language="text",
            )

            st.markdown("**T_GC — Global → Camera**")
            st.code(
                np.array2string(scene["camera_transform_g_c"], precision=6, suppress_small=True),
                language="text",
            )

        with mc2:
            st.markdown("**T_B0 — Base → Joint 0**")
            st.code(
                np.array2string(scene["fk"].transforms[0], precision=6, suppress_small=True),
                language="text",
            )

            st.markdown("**T_B1 — Base → Joint 1**")
            st.code(
                np.array2string(scene["fk"].transforms[1], precision=6, suppress_small=True),
                language="text",
            )

            st.markdown("**T_B2 — Base → Joint 2**")
            st.code(
                np.array2string(scene["fk"].transforms[2], precision=6, suppress_small=True),
                language="text",
            )

        st.markdown("---")
        st.markdown("#### 📐 DH Parameters")
        dh_df = pd.DataFrame({
            "Link": [1, 2, 3],
            "d [m]": [0.35, 0.0, 0.0],
            "a [m]": [0.0, 0.45, 0.30],
            "α [rad]": [f"{np.pi/2:.4f}", "0.0000", "0.0000"],
            "θ offset [rad]": ["0.0000", "0.0000", "0.0000"],
        })
        st.dataframe(dh_df, use_container_width=True, hide_index=True)

    # ── Footer ────────────────────────────────────────────────────────────
    footer()


if __name__ == "__main__":
    main()
