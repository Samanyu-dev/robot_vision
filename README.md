<div align="center">

<!-- HERO HEADER -->
<img src="https://raw.githubusercontent.com/Samanyu-dev/robot_vision/main/assets/banner.png" alt="Robot Vision Lab Banner" width="100%" onerror="this.style.display='none'">

<h1 style="font-family: 'Orbitron', sans-serif; font-weight: 900; font-size: 3.5rem; background: linear-gradient(90deg, #4fc3f7, #ff5ad1, #ffe082); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;">
  🤖 ROBOT VISION LAB
</h1>

<p style="font-family: 'Rajdhani', sans-serif; font-size: 1.4rem; color: #64748b; letter-spacing: 4px; text-transform: uppercase; margin-top: 0.5rem;">
  Premium 3R Manipulator · Wrist Camera · Real-time Projection
</p>

<br>

<!-- BADGES -->
<a href="https://streamlit.io"><img src="https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"></a>
<a href="https://plotly.com"><img src="https://img.shields.io/badge/3D%20Vis-Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white"></a>
<a href="https://opencv.org"><img src="https://img.shields.io/badge/Computer%20Vision-OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white"></a>
<a href="https://numpy.org"><img src="https://img.shields.io/badge/Math-NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white"></a>

<br><br>

<!-- QUICK LINKS -->
<a href="#-live-demo" style="text-decoration: none;">
  <img src="https://img.shields.io/badge/▶%20LIVE%20DEMO-6366f1?style=for-the-badge&color=linear-gradient(135deg,%20%234fc3f7,%20%230288d1)">
</a>
<a href="#-quick-start" style="text-decoration: none;">
  <img src="https://img.shields.io/badge/⚡%20QUICK%20START-69f0ae?style=for-the-badge&color=linear-gradient(135deg,%20%2369f0ae,%20%2300c853)">
</a>
<a href="https://github.com/Samanyu-dev/robot_vision" style="text-decoration: none;">
  <img src="https://img.shields.io/badge/⭐%20GITHUB-ff5ad1?style=for-the-badge&color=linear-gradient(135deg,%20%23ff5ad1,%20%23b71c1c)">
</a>

</div>

---

## 🌌 Overview

**Robot Vision Lab** is a premium, interactive simulation platform for a **3R robotic manipulator** with a wrist-mounted pinhole camera. It bridges robotics kinematics, computer vision projection, and real-time 3D visualization into a single immersive dashboard.

> ⚡ **Not your average Streamlit app.** This feels like a modern AI/robotics product — complete with glassmorphism UI, neon gradients, particle animations, and interactive 3D scenes.

<div align="center">
<table>
<tr>
<td align="center" width="50%">

### 🤖 Robot + Camera
Interactive Plotly 3D scene with articulated links, coordinate frames, and a glowing camera module.

</td>
<td align="center" width="50%">

### 📷 Live Projection
OpenCV-rendered 640×480 image plane showing real-time cube vertex projections with "OUT OF VIEW" warnings.

</td>
</tr>
</table>
</div>

---

## ✨ Features

### 🎨 Premium UI/UX
- **Dark futuristic theme** with gradient backgrounds and glassmorphism cards
- **Custom typography**: Orbitron (sci-fi headers) + Rajdhani (data labels)
- **Animated particle overlay** for a living, breathing interface
- **Neon glow effects** on titles, separators, and hover interactions
- **Responsive metric cards** with gradient top-border reveals

### 🎮 Interactive 3D Scene *(Plotly)*
- **Rotate · Zoom · Pan** the full robot workspace
- **Articulated 3R arm** with 3 revolute joints and DH parameters
- **Glowing magenta camera** module with optical axis visualization
- **Wireframe or solid cube** toggle with 8 tracked vertices
- **RGB coordinate frames** for Global (G), End-Effector (E), and Camera (C)
- **Ground grid** for spatial reference

### 📷 Camera Projection Panel *(OpenCV)*
- **640×480 simulated image plane** with grid overlay
- **Blue projected vertices** and edges for the cube
- **Magenta crosshair** at the principal point
- **Animated "OUT OF VIEW" warning** when vertices leave the frame
- Live pixel coordinate table with visibility checkmarks

### 🎛️ Real-time Controls
| Control | Range | Description |
|---------|-------|-------------|
| θ₁ (Base) | −180° → 180° | Base joint rotation |
| θ₂ (Shoulder) | −120° → 120° | Shoulder joint rotation |
| θ₃ (Wrist) | −120° → 120° | Wrist joint rotation |
| Cube Side | 0.05 → 0.60 m | Object size |
| Cube (X, Y, Z) | Free | Object position in world frame |
| Focal Length | 250 → 1000 px | Camera intrinsics |
| Camera Tilt | −60° → 30° | Wrist camera tilt angle |

### 🎬 Auto Trajectory Animation
- **Sinusoidal motion**: θ₁(t) = 30 + 20·sin(t), θ₂(t) = 45 + 15·sin(2t), θ₃(t) = −20 + 10·cos(t)
- **Play / Pause / Speed controls** in the sidebar
- **Live trajectory tracking** of (u, v) projection centroids

### 📊 Analytics Dashboard
- **5 live metric cards**: Visible Vertices, Camera Z, Image Status, Manipulability, EE→Cube Distance
- **(u, v) Trajectory Plot** — tracks projection path over time with Plotly
- **Position Metrics** — End-effector vs Camera coordinates
- **Distance Metrics** — Base→EE, Base→Cam, Cam→Cube

### 🔥 Jacobian Analysis
- **Plasma heatmap** of the 6×3 geometric Jacobian with value annotations
- **Singular value decomposition** bar chart
- **Manipulability gauge** with progress indicator

### 🎬 GIF Generation
- Pre-render **3D Trajectory GIF** (60 frames @ 15 fps)
- Pre-render **Camera View GIF** (60 frames @ 15 fps)

### 🧮 Matrix Lab
- All homogeneous transforms: **T_BE**, **T_GC**, **T_B0**, **T_B1**, **T_B2**
- Complete **DH Parameter table**

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Samanyu-dev/robot_vision.git
cd robot_vision
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

> 🐧 **For headless Linux servers**, `opencv-python-headless` is used instead of the standard `opencv-python` to avoid `libGL.so.1` errors.

### 3. Launch the App
```bash
streamlit run app.py
```

The dashboard will open at **`http://localhost:8501`**.

---

## 🏗️ Project Structure

```
robot_vision/
│
├── app.py                      ← 🚀 Premium Streamlit dashboard (main entry)
├── requirements.txt            ← Dependencies (Plotly, OpenCV-Headless, Pandas, Kaleido)
│
├── src/
│   ├── __init__.py
│   ├── kinematics.py           ← DH forward kinematics for 3R arm
│   ├── camera.py               ← Camera extrinsics & mount transforms
│   ├── projection.py           ← Pinhole projection (world → image)
│   ├── cube.py                 ← Cube vertex geometry
│   ├── jacobian.py             ← Geometric Jacobian & manipulability
│   ├── visualization.py        ← 🎨 Plotly 3D + OpenCV camera + trajectory plots
│   └── ui_components.py        ← ✨ Premium CSS, animations, layout helpers
│
├── scripts/
│   ├── phase1_forward_kinematics.py
│   ├── phase2_camera_extrinsics.py
│   ├── phase3_projection.py
│   ├── phase4_image_coordinates.py
│   ├── phase5_cube_vertices.py
│   ├── phase6_jacobian.py
│   ├── phase7_trajectory.py
│   ├── phase8_simulation_3d.py
│   └── phase9_camera_view.py
│
├── tests/
│   ├── test_kinematics.py
│   ├── test_camera.py
│   ├── test_projection.py
│   ├── test_cube.py
│   └── test_jacobian.py
│
├── docs/
│   ├── phase_0_system_model.md
│   ├── phase_1_kinematics.md
│   ├── phase_2_camera_extrinsics.md
│   ├── phase_3_projection.md
│   ├── phase_4_image_coordinates.md
│   ├── phase_5_cube_vertices.md
│   ├── phase_6_jacobian.md
│   ├── phase_7_trajectory.md
│   ├── phase_8_simulation_3d.md
│   ├── phase_9_camera_view.md
│   └── live_demo.md
│
└── outputs/
```

---

## 🧠 Technical Stack

<div align="center">

| Layer | Technology |
|-------|-----------|
| **Frontend / UI** | Streamlit + Custom HTML/CSS/JS |
| **3D Visualization** | Plotly Graph Objects (WebGL-accelerated) |
| **Image Rendering** | OpenCV (headless) + NumPy |
| **Math & Kinematics** | NumPy + SciPy |
| **Data Handling** | Pandas |
| **Static Plots** | Matplotlib |
| **GIF Export** | Pillow + Kaleido |

</div>

---

## 📸 Screenshots

> *Replace these placeholders with actual screenshots after running the app*

<div align="center">
<table>
<tr>
<td align="center" width="50%">
<b>🎮 Live 3D Scene</b><br>
<img src="outputs/robot_trajectory_3d.gif" alt="3D Robot Trajectory" width="100%" style="border-radius: 12px; border: 1px solid #1e293b;">
</td>
<td align="center" width="50%">
<b>📷 Camera View</b><br>
<img src="outputs/camera_view.gif" alt="Camera Projection" width="100%" style="border-radius: 12px; border: 1px solid #1e293b;">
</td>
</tr>
</table>
</div>

---

## 🎯 Key Concepts Demonstrated

1. **DH Parameter Forward Kinematics** — T_BE from 3 revolute joints
2. **Camera Extrinsics** — T_GC via end-effector mount with tilt offset
3. **Pinhole Projection** — World → Camera → Image plane via K [R|t]
4. **Visibility Testing** — In-front and in-bounds checks per vertex
5. **Geometric Jacobian** — 6×3 matrix relating joint velocities to EE spatial velocity
6. **Manipulability** — Yoshikawa measure: √det(JᵀJ)

---

## 🛠️ Development

### Running Tests
```bash
pytest tests/
```

### Phase Scripts
Each `scripts/phase*.py` corresponds to a robotics concept doc in `docs/`:
```bash
python scripts/phase1_forward_kinematics.py
python scripts/phase8_simulation_3d.py
```

---

## 🌐 Host the Landing Page (Free via GitHub Pages)

The project includes a beautiful standalone HTML landing page at `docs/demo_landing.html`. You can host it **for free** in under 2 minutes:

### Option A: GitHub Pages (Recommended — Free & Fast)
1. Go to your repo → **Settings** → **Pages** (left sidebar)
2. Under **Build and deployment** → Source, select **Deploy from a branch**
3. Select branch: **`main`** → folder: **`/docs`** → click **Save**
4. Wait ~30 seconds, then visit:
   ```
   https://samanyu-dev.github.io/robot_vision/demo_landing.html
   ```

> 💡 **Tip**: If you want the landing page at the root URL, rename `docs/demo_landing.html` to `docs/index.html`.

### Option B: Netlify Drop (Drag & Drop)
1. Go to [netlify.com/drop](https://app.netlify.com/drop)
2. Drag the `docs/` folder onto the page
3. Get an instant live URL (free forever)

### Option C: Vercel
1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel --cwd docs` from the project root
3. Get a `.vercel.app` URL instantly

---

## 📝 Citation / Credits

Built with ❤️ by **Samanyu** as part of a robotics + computer vision coursework project.

- **Repo**: [github.com/Samanyu-dev/robot_vision](https://github.com/Samanyu-dev/robot_vision)
- **Framework**: [Streamlit](https://streamlit.io)
- **3D Engine**: [Plotly](https://plotly.com/python/3d-charts/)

---

<div align="center">

<p style="font-family: 'Orbitron', sans-serif; font-size: 1.2rem; color: #4fc3f7; letter-spacing: 3px;">
  🤖 ROBOT VISION LAB · PREMIUM EDITION v3.0
</p>

<p style="font-family: 'Rajdhani', sans-serif; color: #475569; letter-spacing: 2px;">
  Built with Streamlit · Enhanced with Plotly · Powered by NumPy
</p>

</div>
