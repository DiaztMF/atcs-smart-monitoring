import os
# Set writable config dir for Ultralytics in serverless/container environments
os.environ["YOLO_CONFIG_DIR"] = "/tmp/Ultralytics"
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"

import gradio as gr
from fastapi.responses import HTMLResponse
from app.main import app as fastapi_app
from app.core.config import settings

@fastapi_app.get("/", response_class=HTMLResponse)
async def root_dashboard():
    return f"""
    <!DOCTYPE html>
    <html>
      <head>
        <title>{settings.PROJECT_NAME} — Backend API</title>
        <style>
          body {{ background: #0a0d14; color: #f3f4f6; font-family: system-ui, sans-serif; padding: 2rem; }}
          .card {{ background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 1.5rem; max-width: 600px; margin: 0 auto; }}
          h1 {{ color: #10b981; font-size: 1.5rem; }}
          a {{ color: #38bdf8; text-decoration: none; }}
          a:hover {{ text-decoration: underline; }}
          ul {{ list-style: none; padding-left: 0; }}
          li {{ padding: 0.5rem 0; border-bottom: 1px solid #1f2937; }}
          .status {{ display: inline-block; padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; background: #064e3b; color: #34d399; }}
        </style>
      </head>
      <body>
        <div class="card">
          <h1>🚦 {settings.PROJECT_NAME}</h1>
          <p>Status: <span class="status">● ONLINE / RUNNING</span></p>
          <p>Real-Time Computer Vision & Traffic Load Monitoring (SMP) Backend API.</p>
          <h3>Active Endpoints:</h3>
          <ul>
            <li>📹 <a href="/api/v1/stream" target="_blank">Live MJPEG Video Stream (/api/v1/stream)</a></li>
            <li>📊 <a href="/api/v1/roi" target="_blank">ROI Coordinates API (/api/v1/roi)</a></li>
            <li>💓 <a href="/api/v1/health" target="_blank">Health Check (/api/v1/health)</a></li>
            <li>⚡ <b>WebSocket Broadcaster:</b> <code>/ws/metrics</code></li>
            <li>🎛️ <a href="/status" target="_blank">Gradio Status (/status)</a></li>
          </ul>
        </div>
      </body>
    </html>
    """

# Create a clean Gradio interface for HF Spaces health checks at /status
with gr.Blocks(title=settings.PROJECT_NAME) as demo:
    gr.Markdown(f"# 🚦 {settings.PROJECT_NAME} — Backend API")
    gr.Markdown("Layanan Backend Real-Time Computer Vision & Traffic Load Monitoring (SMP) aktif dan berjalan.")

# Mount Gradio onto FastAPI app at /status
app = gr.mount_gradio_app(fastapi_app, demo, path="/status")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
