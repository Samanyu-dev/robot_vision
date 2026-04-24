"""Premium UI components: CSS, animations, and layout helpers."""

from __future__ import annotations

import base64
import io
from typing import Sequence

import numpy as np
import streamlit as st

# ---------------------------------------------------------------------------
# Premium Dark Theme CSS
# ---------------------------------------------------------------------------

PREMIUM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

/* ── Global dark theme ─────────────────────────────────────────────── */
.stApp {
    background: linear-gradient(135deg, #070b14 0%, #0f172a 40%, #111827 100%);
    color: #e2e8f0;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: #0a0e17;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #4fc3f7, #ff5ad1);
    border-radius: 4px;
}

/* ── Hero header ───────────────────────────────────────────────────── */
.main-title {
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    font-size: 3rem;
    background: linear-gradient(90deg, #4fc3f7, #ff5ad1, #ffe082);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin-bottom: 0.2rem;
    letter-spacing: 3px;
    animation: titleGlow 3s ease-in-out infinite alternate;
}

@keyframes titleGlow {
    from { filter: drop-shadow(0 0 8px rgba(79,195,247,0.3)); }
    to   { filter: drop-shadow(0 0 25px rgba(255,90,209,0.6)); }
}

.subtitle {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.3rem;
    color: #64748b;
    text-align: center;
    margin-bottom: 2.5rem;
    letter-spacing: 5px;
    text-transform: uppercase;
    font-weight: 500;
}

.hero-badge {
    display: inline-block;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.65rem;
    color: #0f172a;
    background: linear-gradient(90deg, #4fc3f7, #69f0ae);
    padding: 3px 12px;
    border-radius: 12px;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 700;
}

/* ── Glassmorphism cards ───────────────────────────────────────────── */
.glass-card {
    background: linear-gradient(135deg, rgba(26,35,50,0.7) 0%, rgba(15,23,42,0.9) 100%);
    border: 1px solid rgba(79,195,247,0.15);
    border-radius: 16px;
    padding: 1.25rem;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    transition: all 0.3s ease;
}
.glass-card:hover {
    border-color: rgba(79,195,247,0.4);
    box-shadow: 0 8px 40px rgba(79,195,247,0.15);
    transform: translateY(-2px);
}

/* ── Metric cards ──────────────────────────────────────────────────── */
.metric-card {
    background: linear-gradient(135deg, #1a2332 0%, #0f141d 100%);
    border: 1px solid #2f3b4c;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, #4fc3f7, #ff5ad1);
    opacity: 0;
    transition: opacity 0.3s ease;
}
.metric-card:hover::before {
    opacity: 1;
}
.metric-card:hover {
    border-color: #4fc3f7;
    box-shadow: 0 0 20px rgba(79,195,247,0.15);
}
.metric-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
}
.metric-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.8rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
}

/* ── Sidebar styling ──────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0e17 0%, #111827 100%);
    border-right: 1px solid #1e293b;
}
[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}
.sidebar-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.95rem;
    color: #4fc3f7;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 1.5rem 0 0.8rem 0;
    border-bottom: 1px solid #1e293b;
    padding-bottom: 0.5rem;
}
.sidebar-section {
    background: rgba(15,23,42,0.5);
    border-radius: 10px;
    padding: 0.75rem;
    margin-bottom: 0.75rem;
    border: 1px solid rgba(47,59,76,0.3);
}

/* ── Slider styling ───────────────────────────────────────────────── */
.stSlider > div > div > div > div {
    background: linear-gradient(90deg, #4fc3f7, #ff5ad1) !important;
}

/* ── Button styling ───────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #4fc3f7 0%, #0288d1 100%) !important;
    color: white !important;
    font-family: 'Orbitron', sans-serif !important;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    font-size: 0.75rem !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.2rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative;
    overflow: hidden;
}
.stButton > button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 8px 25px rgba(79,195,247,0.4) !important;
}
.stButton > button:active {
    transform: translateY(0) scale(0.98);
}

/* Danger / stop button */
.btn-danger > button {
    background: linear-gradient(135deg, #ff5252 0%, #b71c1c 100%) !important;
}
.btn-danger > button:hover {
    box-shadow: 0 8px 25px rgba(255,82,82,0.4) !important;
}

/* Success / play button */
.btn-success > button {
    background: linear-gradient(135deg, #69f0ae 0%, #00c853 100%) !important;
    color: #0f172a !important;
}
.btn-success > button:hover {
    box-shadow: 0 8px 25px rgba(105,240,174,0.4) !important;
}

/* ── Toggle styling ───────────────────────────────────────────────── */
.stCheckbox > label {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    color: #94a3b8 !important;
}

/* ── Tab styling ──────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background: #0a0e17;
    padding: 10px 12px;
    border-radius: 14px;
    border: 1px solid #1e293b;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.78rem;
    letter-spacing: 1.5px;
    background: #111827;
    border-radius: 10px;
    color: #64748b;
    border: 1px solid #1e293b;
    transition: all 0.3s ease;
    padding: 10px 18px !important;
    text-transform: uppercase;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #4fc3f7;
    border-color: #4fc3f7;
    background: #1a2332;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4fc3f7 0%, #0288d1 100%) !important;
    color: white !important;
    border-color: #4fc3f7 !important;
    box-shadow: 0 4px 15px rgba(79,195,247,0.3);
}

/* ── Code / data styling ──────────────────────────────────────────── */
.stCodeBlock {
    background: #070b14 !important;
    border: 1px solid #1e293b;
    border-radius: 10px;
}
.stDataFrame {
    background: #0a0e17 !important;
}
.stDataFrame th {
    background: #1a2332 !important;
    color: #4fc3f7 !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.stDataFrame td {
    color: #cbd5e1 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.85rem !important;
}

/* ── Expander styling ─────────────────────────────────────────────── */
.streamlit-expanderHeader {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.85rem;
    color: #4fc3f7;
    background: linear-gradient(135deg, #1a2332 0%, #0f141d 100%);
    border-radius: 10px;
    border: 1px solid #2f3b4c;
    letter-spacing: 1px;
}

/* ── Progress bar ─────────────────────────────────────────────────── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #4fc3f7, #ff5ad1) !important;
    border-radius: 4px;
}

/* ── Selectbox / number input ─────────────────────────────────────── */
.stSelectbox > div > div,
.stNumberInput > div > div {
    background: #0a0e17 !important;
    border-color: #1e293b !important;
    border-radius: 8px !important;
}

/* ── Separator glow ───────────────────────────────────────────────── */
.glow-sep {
    height: 1px;
    background: linear-gradient(90deg, transparent, #4fc3f7, #ff5ad1, transparent);
    margin: 1.5rem 0;
    border: none;
}

/* ── Warning pulse animation ──────────────────────────────────────── */
@keyframes pulseWarning {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
.pulse-warning {
    animation: pulseWarning 1.5s ease-in-out infinite;
}

/* ── Footer ───────────────────────────────────────────────────────── */
.footer-text {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.8rem;
    color: #475569;
    text-align: center;
    letter-spacing: 2px;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #1e293b;
}

/* ── Floating particles canvas ────────────────────────────────────── */
#particle-canvas {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 9999;
}
</style>

<canvas id="particle-canvas"></canvas>
<script>
const canvas = document.getElementById('particle-canvas');
if (canvas) {
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const particles = [];
    const colors = ['#4fc3f7', '#ff5ad1', '#ffe082', '#69f0ae'];

    for (let i = 0; i < 60; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.4,
            vy: (Math.random() - 0.5) * 0.4,
            size: Math.random() * 2 + 0.5,
            color: colors[Math.floor(Math.random() * colors.length)],
            alpha: Math.random() * 0.4 + 0.1
        });
    }

    function animateParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;
            if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.globalAlpha = p.alpha;
            ctx.fill();
        });
        ctx.globalAlpha = 1;
        requestAnimationFrame(animateParticles);
    }
    animateParticles();
}
</script>
"""

# ---------------------------------------------------------------------------
# Layout helpers
# ---------------------------------------------------------------------------


def inject_premium_css() -> None:
    """Inject the premium dark CSS into Streamlit."""
    st.markdown(PREMIUM_CSS, unsafe_allow_html=True)


def hero_header() -> None:
    """Render the glowing hero header."""
    st.markdown(
        '<div style="text-align:center;margin-bottom:0.3rem;">'
        '<span class="hero-badge">Premium Edition v3.0</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="main-title">🤖 ROBOT VISION LAB</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">3R Manipulator · Wrist Camera · Real-time Projection</div>',
        unsafe_allow_html=True,
    )


def metric_card_html(label: str, value: str, color: str) -> str:
    """Return HTML for a single metric card."""
    return (
        f'<div class="metric-card">'
        f'<div class="metric-value" style="color:{color};">{value}</div>'
        f'<div class="metric-label">{label}</div>'
        f'</div>'
    )


def render_metric_row(
    labels: Sequence[str],
    values: Sequence[str],
    colors: Sequence[str],
) -> None:
    """Render a row of metric cards using Streamlit columns."""
    cols = st.columns(len(labels))
    for col, label, value, color in zip(cols, labels, values, colors):
        with col:
            st.markdown(metric_card_html(label, value, color), unsafe_allow_html=True)


def glass_container() -> st.container:
    """Return a Streamlit container wrapped in a glassmorphism card."""
    return st.container()


def footer() -> None:
    """Render the app footer."""
    st.markdown('<div class="glow-sep"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="footer-text">'
        '🤖 Robot Vision Lab · Built with Streamlit · Premium Edition v3.0'
        '</div>',
        unsafe_allow_html=True,
    )
