import gradio as gr
from app.main import app as fastapi_app
from app.core.config import settings

# Create a clean Gradio interface for HF Spaces
with gr.Blocks(title=settings.PROJECT_NAME) as demo:
    gr.Markdown(f"# 🚦 {settings.PROJECT_NAME} — Backend API")
    gr.Markdown("Layanan Backend Real-Time Computer Vision & Traffic Load Monitoring (SMP) aktif dan berjalan.")
    with gr.Row():
        gr.Markdown("""
        ### Endpoint Aktif:
        - 📹 **Live MJPEG Stream:** [`/api/v1/stream`](/api/v1/stream)
        - 📊 **REST ROI Config:** [`/api/v1/roi`](/api/v1/roi)
        - 💓 **Health Check:** [`/api/v1/health`](/api/v1/health)
        - ⚡ **WebSocket Broadcaster:** `/ws/metrics`
        """)

# Mount Gradio onto FastAPI app
app = gr.mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
