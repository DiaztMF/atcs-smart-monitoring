import os
import sys

# Set writable directories for container runtime
os.environ["YOLO_CONFIG_DIR"] = "/tmp"
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"

import gradio as gr
from app.main import app as fastapi_app
from app.core.config import settings

# Create a clean Gradio interface for HF Spaces at root
with gr.Blocks(title=settings.PROJECT_NAME) as demo:
    gr.Markdown(f"# 🚦 {settings.PROJECT_NAME} — Backend API")
    gr.Markdown("Real-Time Computer Vision & Traffic Load Monitoring (SMP) Service is **ONLINE & RUNNING**.")
    with gr.Row():
        gr.Markdown("""
        ### Endpoint Aktif:
        - 📹 **Live MJPEG Stream:** [`/api/v1/stream`](/api/v1/stream)
        - 📊 **REST ROI Config:** [`/api/v1/roi`](/api/v1/roi)
        - 💓 **Health Check:** [`/api/v1/health`](/api/v1/health)
        - ⚡ **WebSocket Broadcaster:** `/ws/metrics`
        """)

# Mount Gradio at root so Hugging Face supervisor gets /config and status checks
app = gr.mount_gradio_app(fastapi_app, demo, path="")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
