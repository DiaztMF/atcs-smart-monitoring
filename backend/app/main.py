from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from app.core.config import settings
from app.core.logging import logger
from app.services.detector import TrafficDetector
from app.services.stream_reader import StreamReaderWorker
from app.api.endpoints import router as api_router
from app.api.websocket import router as ws_router

detector_instance = TrafficDetector(model_name="yolo11n.pt")
stream_worker = StreamReaderWorker(detector=detector_instance)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Smart Traffic Monitoring Server...")
    stream_worker.start()
    yield
    logger.info("Shutting down Smart Traffic Monitoring Server...")
    stream_worker.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.BACKEND_CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
@app.head("/")
async def root_status():
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
          <p>Real-Time Computer Vision & Traffic Load Monitoring (SMP) Backend Service.</p>
          <h3>Active Endpoints:</h3>
          <ul>
            <li>📹 <a href="/api/v1/stream" target="_blank">Live MJPEG Stream (/api/v1/stream)</a></li>
            <li>📊 <a href="/api/v1/roi" target="_blank">ROI Coordinates API (/api/v1/roi)</a></li>
            <li>💓 <a href="/api/v1/health" target="_blank">Health Check (/api/v1/health)</a></li>
            <li>⚡ <b>WebSocket Broadcaster:</b> <code>/ws/metrics</code></li>
          </ul>
        </div>
      </body>
    </html>
    """

@app.get("/healthz")
async def healthz():
    return JSONResponse(content={"status": "ok", "service": settings.PROJECT_NAME})

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(ws_router)
