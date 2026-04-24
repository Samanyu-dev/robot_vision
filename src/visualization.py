"""3D visualization and camera rendering utilities.

Provides:
- Interactive Plotly 3D robot scene
- OpenCV-based camera projection frame
- Trajectory analytics plots
"""

from __future__ import annotations

from typing import Sequence

import cv2
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from cube import CUBE_EDGES
from kinematics import ForwardKinematicsResult

# ---------------------------------------------------------------------------
# Plotly 3D Scene
# ---------------------------------------------------------------------------


def _add_coordinate_frame(
    fig: go.Figure,
    transform: np.ndarray,
    scale: float,
    label: str,
    origin_color: str = "white",
) -> None:
    """Add a RGB coordinate frame to a Plotly figure."""
    origin = transform[:3, 3]
    axes = transform[:3, :3]
    colors = ("#ff5252", "#69f0ae", "#40c4ff")
    names = (f"{label}_x", f"{label}_y", f"{label}_z")

    for i, (color, name) in enumerate(zip(colors, names)):
        direction = axes[:, i] * scale
        fig.add_trace(
            go.Scatter3d(
                x=[origin[0], origin[0] + direction[0]],
                y=[origin[1], origin[1] + direction[1]],
                z=[origin[2], origin[2] + direction[2]],
                mode="lines",
                line=dict(color=color, width=4),
                name=name,
                showlegend=False,
                hoverinfo="skip",
            )
        )

    fig.add_trace(
        go.Scatter3d(
            x=[origin[0]],
            y=[origin[1]],
            z=[origin[2]],
            mode="markers+text",
            marker=dict(size=3, color=origin_color),
            text=[label],
            textposition="top center",
            textfont=dict(size=10, color=origin_color, family="Orbitron"),
            showlegend=False,
            hoverinfo="skip",
        )
    )


def build_robot_plotly(
    fk: ForwardKinematicsResult,
    cube_vertices: np.ndarray,
    camera_transform_g_c: np.ndarray,
    show_frames: bool = True,
    wireframe_cube: bool = False,
) -> go.Figure:
    """Build an interactive Plotly 3D scene."""
    origins = fk.origins
    camera_origin = camera_transform_g_c[:3, 3]
    optical_axis = camera_transform_g_c[:3, 2]

    fig = go.Figure()

    # Ground grid
    grid_range = np.linspace(-0.5, 1.8, 24)
    for y_val in np.linspace(-0.8, 0.8, 9):
        fig.add_trace(
            go.Scatter3d(
                x=grid_range,
                y=[y_val] * len(grid_range),
                z=[0.0] * len(grid_range),
                mode="lines",
                line=dict(color="#1e293b", width=1),
                showlegend=False,
                hoverinfo="skip",
            )
        )
    for x_val in np.linspace(-0.5, 1.8, 24):
        fig.add_trace(
            go.Scatter3d(
                x=[x_val] * len(grid_range),
                y=grid_range,
                z=[0.0] * len(grid_range),
                mode="lines",
                line=dict(color="#1e293b", width=1),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    # Robot arm links
    fig.add_trace(
        go.Scatter3d(
            x=origins[:, 0],
            y=origins[:, 1],
            z=origins[:, 2],
            mode="lines+markers",
            line=dict(color="#4fc3f7", width=8),
            marker=dict(size=6, color="white", line=dict(color="#0f172a", width=2)),
            name="Robot Arm",
            hovertemplate="Link %{pointNumber}<br>X: %{x:.3f}<br>Y: %{y:.3f}<br>Z: %{z:.3f}<extra></extra>",
        )
    )

    # Camera
    fig.add_trace(
        go.Scatter3d(
            x=[camera_origin[0]],
            y=[camera_origin[1]],
            z=[camera_origin[2]],
            mode="markers",
            marker=dict(
                size=10,
                color="#ff5ad1",
                symbol="square",
                line=dict(color="white", width=2),
            ),
            name="Camera",
            hovertemplate="Camera<br>X: %{x:.3f}<br>Y: %{y:.3f}<br>Z: %{z:.3f}<extra></extra>",
        )
    )

    # Optical axis
    fig.add_trace(
        go.Scatter3d(
            x=[camera_origin[0], camera_origin[0] + optical_axis[0] * 0.3],
            y=[camera_origin[1], camera_origin[1] + optical_axis[1] * 0.3],
            z=[camera_origin[2], camera_origin[2] + optical_axis[2] * 0.3],
            mode="lines",
            line=dict(color="#ff5ad1", width=4, dash="solid"),
            name="Optical Axis",
            showlegend=False,
            hoverinfo="skip",
        )
    )

    # Cube edges
    for start, end in CUBE_EDGES:
        segment = cube_vertices[[start, end]]
        fig.add_trace(
            go.Scatter3d(
                x=segment[:, 0],
                y=segment[:, 1],
                z=segment[:, 2],
                mode="lines",
                line=dict(color="#ff6f61", width=3),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    # Cube vertices
    fig.add_trace(
        go.Scatter3d(
            x=cube_vertices[:, 0],
            y=cube_vertices[:, 1],
            z=cube_vertices[:, 2],
            mode="markers",
            marker=dict(size=4, color="#ff6f61", line=dict(color="white", width=1)),
            name="Cube",
            hovertemplate="Vertex %{pointNumber}<br>X: %{x:.3f}<br>Y: %{y:.3f}<br>Z: %{z:.3f}<extra></extra>",
        )
    )

    # Cube faces (if solid)
    if not wireframe_cube:
        faces = [
            [0, 1, 2, 3],
            [4, 5, 6, 7],
            [0, 1, 5, 4],
            [2, 3, 7, 6],
            [1, 2, 6, 5],
            [0, 3, 7, 4],
        ]
        for face in faces:
            xs = [cube_vertices[i][0] for i in face] + [cube_vertices[face[0]][0]]
            ys = [cube_vertices[i][1] for i in face] + [cube_vertices[face[0]][1]]
            zs = [cube_vertices[i][2] for i in face] + [cube_vertices[face[0]][2]]
            fig.add_trace(
                go.Mesh3d(
                    x=xs[:-1],
                    y=ys[:-1],
                    z=zs[:-1],
                    opacity=0.15,
                    color="#ff6f61",
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

    # Coordinate frames
    if show_frames:
        _add_coordinate_frame(fig, np.eye(4), scale=0.18, label="G", origin_color="#4fc3f7")
        _add_coordinate_frame(fig, fk.end_effector_transform, scale=0.14, label="E", origin_color="#69f0ae")
        _add_coordinate_frame(fig, camera_transform_g_c, scale=0.12, label="C", origin_color="#ff5ad1")

    # Scene layout
    all_points = np.vstack([origins, cube_vertices, camera_origin.reshape(1, 3)])
    mins = all_points.min(axis=0)
    maxs = all_points.max(axis=0)
    center = (mins + maxs) / 2.0
    radius = max(float((maxs - mins).max()) / 2.0, 0.6)

    fig.update_layout(
        scene=dict(
            xaxis=dict(
                range=[center[0] - radius, center[0] + radius],
                backgroundcolor="#0b1017",
                gridcolor="#1e293b",
                showbackground=True,
                zerolinecolor="#334155",
                title=dict(text="X [m]", font=dict(color="#94a3b8")),
                tickfont=dict(color="#64748b"),
            ),
            yaxis=dict(
                range=[center[1] - radius, center[1] + radius],
                backgroundcolor="#0b1017",
                gridcolor="#1e293b",
                showbackground=True,
                zerolinecolor="#334155",
                title=dict(text="Y [m]", font=dict(color="#94a3b8")),
                tickfont=dict(color="#64748b"),
            ),
            zaxis=dict(
                range=[max(0.0, center[2] - radius), center[2] + radius],
                backgroundcolor="#0b1017",
                gridcolor="#1e293b",
                showbackground=True,
                zerolinecolor="#334155",
                title=dict(text="Z [m]", font=dict(color="#94a3b8")),
                tickfont=dict(color="#64748b"),
            ),
            aspectmode="cube",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.0)),
            bgcolor="#0b1017",
        ),
        paper_bgcolor="#0b1017",
        plot_bgcolor="#0b1017",
        margin=dict(l=0, r=0, b=0, t=30),
        title=dict(
            text="🤖 Interactive 3R Robot + Wrist Camera + Cube",
            font=dict(size=16, color="white", family="Orbitron"),
            x=0.5,
        ),
        legend=dict(
            font=dict(color="white", family="Rajdhani"),
            bgcolor="rgba(15,23,42,0.8)",
            bordercolor="#1e293b",
            borderwidth=1,
        ),
        hoverlabel=dict(
            bgcolor="#0f172a",
            bordercolor="#4fc3f7",
            font=dict(color="white", family="Rajdhani"),
        ),
        height=650,
    )

    return fig


# ---------------------------------------------------------------------------
# OpenCV Camera View
# ---------------------------------------------------------------------------


def build_camera_frame_opencv(
    projected_pixels: np.ndarray,
    visibility_mask: np.ndarray,
    width: int = 640,
    height: int = 480,
    cx: float = 320.0,
    cy: float = 240.0,
    show_grid: bool = True,
) -> np.ndarray:
    """Render a simulated camera image plane using OpenCV."""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:, :] = (11, 16, 23)  # BGR dark background #0b1017

    # Grid
    if show_grid:
        grid_step = 40
        for x in range(0, width + 1, grid_step):
            cv2.line(frame, (x, 0), (x, height), (30, 41, 58), 1)
        for y in range(0, height + 1, grid_step):
            cv2.line(frame, (0, y), (width, y), (30, 41, 58), 1)

    # Image border
    cv2.rectangle(frame, (0, 0), (width - 1, height - 1), (255, 255, 255), 2)

    # Principal point crosshair
    cross_len = 15
    cv2.line(frame, (int(cx) - cross_len, int(cy)), (int(cx) + cross_len, int(cy)), (209, 90, 255), 2)
    cv2.line(frame, (int(cx), int(cy) - cross_len), (int(cx), int(cy) + cross_len), (209, 90, 255), 2)
    cv2.circle(frame, (int(cx), int(cy)), 4, (209, 90, 255), -1)

    # Cube edges
    for start, end in CUBE_EDGES:
        if visibility_mask[start] and visibility_mask[end]:
            p1 = projected_pixels[start]
            p2 = projected_pixels[end]
            if not (np.isnan(p1).any() or np.isnan(p2).any()):
                cv2.line(
                    frame,
                    (int(p1[0]), int(p1[1])),
                    (int(p2[0]), int(p2[1])),
                    (247, 195, 79),  # cyan-ish in BGR
                    2,
                    cv2.LINE_AA,
                )

    # Projected vertices
    for i, (pixel, visible) in enumerate(zip(projected_pixels, visibility_mask)):
        if visible and not np.isnan(pixel).any():
            cv2.circle(
                frame,
                (int(pixel[0]), int(pixel[1])),
                5,
                (247, 195, 79),
                -1,
                cv2.LINE_AA,
            )
            cv2.circle(
                frame,
                (int(pixel[0]), int(pixel[1])),
                5,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

    # "OUT OF VIEW" warning
    visible_count = int(visibility_mask.sum())
    if visible_count < 8:
        warning_text = f"⚠️ OBJECT OUT OF VIEW — {visible_count}/8 vertices visible"
        text_size = cv2.getTextSize(warning_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        tx = (width - text_size[0]) // 2
        ty = height - 30

        # Glowing background
        cv2.rectangle(frame, (tx - 10, ty - text_size[1] - 10), (tx + text_size[0] + 10, ty + 10), (0, 0, 80), -1)
        cv2.rectangle(frame, (tx - 10, ty - text_size[1] - 10), (tx + text_size[0] + 10, ty + 10), (0, 0, 255), 2)
        cv2.putText(frame, warning_text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)

    return frame


# ---------------------------------------------------------------------------
# Trajectory Analytics
# ---------------------------------------------------------------------------


def build_trajectory_plotly(
    uv_history: Sequence[tuple[float, float]],
    width: int = 640,
    height: int = 480,
) -> go.Figure:
    """Build a live trajectory plot of (u, v) pixel coordinates."""
    fig = go.Figure()

    if len(uv_history) > 1:
        u_vals = [p[0] for p in uv_history]
        v_vals = [p[1] for p in uv_history]

        # Trajectory line with gradient color
        fig.add_trace(
            go.Scatter(
                x=u_vals,
                y=v_vals,
                mode="lines+markers",
                line=dict(color="#4fc3f7", width=2),
                marker=dict(size=4, color="#ff5ad1"),
                name="Trajectory",
                hovertemplate="u: %{x:.1f}<br>v: %{y:.1f}<extra></extra>",
            )
        )

        # Current point
        fig.add_trace(
            go.Scatter(
                x=[u_vals[-1]],
                y=[v_vals[-1]],
                mode="markers",
                marker=dict(size=12, color="#69f0ae", symbol="star", line=dict(color="white", width=2)),
                name="Current",
                hovertemplate="Current<br>u: %{x:.1f}<br>v: %{y:.1f}<extra></extra>",
            )
        )

    # Image boundary box
    fig.add_trace(
        go.Scatter(
            x=[0, width, width, 0, 0],
            y=[0, 0, height, height, 0],
            mode="lines",
            line=dict(color="white", width=1, dash="dot"),
            name="Image Bounds",
            hoverinfo="skip",
        )
    )

    # Principal point
    cx, cy = width / 2, height / 2
    fig.add_trace(
        go.Scatter(
            x=[cx],
            y=[cy],
            mode="markers",
            marker=dict(size=8, color="#ff5ad1", symbol="cross"),
            name="Principal Point",
            hoverinfo="skip",
        )
    )

    fig.update_layout(
        xaxis=dict(
            range=[-50, width + 50],
            title="u [px]",
            color="white",
            gridcolor="#1e293b",
            zerolinecolor="#334155",
        ),
        yaxis=dict(
            range=[height + 50, -50],
            title="v [px]",
            color="white",
            gridcolor="#1e293b",
            zerolinecolor="#334155",
        ),
        paper_bgcolor="#0b1017",
        plot_bgcolor="#0b1017",
        font=dict(color="white", family="Rajdhani"),
        margin=dict(l=50, r=20, b=50, t=40),
        title=dict(
            text="📈 (u, v) Projection Trajectory",
            font=dict(size=14, color="white", family="Orbitron"),
            x=0.5,
        ),
        legend=dict(
            font=dict(color="white", family="Rajdhani"),
            bgcolor="rgba(15,23,42,0.8)",
            bordercolor="#1e293b",
            borderwidth=1,
        ),
        height=450,
    )

    return fig
