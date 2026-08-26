from typing import List
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    PROJECT_NAME: str = "Smart Traffic Monitoring"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["*"]
    
    # Video source: FLV stream URL or local fallback sample file
    VIDEO_STREAM_URL: str = "http://bptdjatengdiy.dephub.go.id:8000/live/atcs_surakarta_balaikota.flv"
    FALLBACK_VIDEO_PATH: str = "sample_data/synthetic_traffic.mp4"
    ROI_PERSISTENCE_PATH: str = "default_roi.json"
    
    TARGET_FPS: int = 12
    STREAM_WIDTH: int = 640
    STREAM_HEIGHT: int = 360
    JPEG_QUALITY: int = 65
    
    # Tracking constants
    TTL_FRAME_PURGE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = AppSettings()
