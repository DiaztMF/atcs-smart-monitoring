from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(ws_router)
