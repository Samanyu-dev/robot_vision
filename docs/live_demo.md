# Live Demo Deployment

## Recommended Public Demo

Use Streamlit Community Cloud as the primary live demo.

Why:

- it runs this Python project directly from GitHub
- it supports sliders and Matplotlib figures
- it creates a shareable `streamlit.app` link
- it is the fastest path for a robotics vision demo

Official docs:

- Streamlit Community Cloud deployment: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- Streamlit Community Cloud overview: https://docs.streamlit.io/deploy/streamlit-community-cloud

## Entry Point

The live app entry point is:

```text
app.py
```

The app includes:

- joint sliders for `theta_1`, `theta_2`, and `theta_3`
- cube size and world-center controls
- camera focal-length and tilt controls
- 3D robot/camera/cube visualization
- 640 x 480 image-plane projection view
- visible vertex count and out-of-view status

## Local Run

Install dependencies:

```bash
.venv/bin/python -m pip install -r requirements.txt
```

Run the app locally:

```bash
.venv/bin/streamlit run app.py
```

Open the local URL printed by Streamlit.

## Streamlit Community Cloud Steps

1. Go to https://share.streamlit.io.
2. Sign in with GitHub.
3. Click `Create app`.
4. Choose repository:

```text
Samanyu-dev/robot_vision
```

5. Choose branch:

```text
main
```

6. Choose app file:

```text
app.py
```

7. Deploy.
8. Copy the generated `streamlit.app` URL into the README live-demo section.

## Hugging Face Spaces Alternative

Hugging Face Spaces also supports Streamlit apps.

Official docs:

- https://huggingface.co/docs/hub/spaces-sdks-streamlit

Use this if you want a profile-hosted demo at:

```text
huggingface.co/spaces/<username>/<space-name>
```

## GitHub Pages Alternative

GitHub Pages is better for a static JavaScript or Three.js version of the demo.

Official docs:

- https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site

Use this later if the project gets a pure browser-based simulator.

## README Badge

After deploying, replace the placeholder URL in `README.md` with the real Streamlit URL.

Badge template:

```markdown
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-demo.streamlit.app)
```

