from typing import List, Tuple, Dict, Any, Optional
from pydantic import BaseModel, field_validator
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.core.state import global_state
from app.services.mjpeg_stream import generate_mjpeg_frames

router = APIRouter()

class ROIModel(BaseModel):
    inbound: List[Tuple[float, float]]
    outbound: List[Tuple[float, float]]

    @field_validator("inbound", "outbound")
    @classmethod
    def validate_polygon_points(cls, v: List[Tuple[float, float]], info) -> List[Tuple[float, float]]:
        # Allow empty list (for clearing ROI)
        if len(v) == 0:
            return v
        if len(v) < 3:
            raise ValueError(f"Polygon for '{info.field_name}' must have at least 3 points to form a valid ROI contour (received {len(v)}).")
        for idx, pt in enumerate(v):
            if not (0.0 <= pt[0] <= 1.0 and 0.0 <= pt[1] <= 1.0):
                raise ValueError(f"Point at index {idx} in '{info.field_name}' with coordinates {pt} is outside normalized range [0.0, 1.0].")
        return v

class StreamSourceModel(BaseModel):
    url: str
    name: Optional[str] = "Custom Stream"

@router.get("/health")
async def health_check():
    is_active, fps = global_state.get_stream_status()
    active_stream = global_state.get_active_stream()
    return {
        "status": "ok",
        "stream_active": is_active,
        "fps": fps,
        "active_stream": active_stream
    }

@router.get("/stream-source")
async def get_stream_source():
    return {
        "active_source": global_state.get_active_stream(),
        "presets": global_state.get_cctv_presets()
    }

@router.post("/stream-source")
async def switch_stream_source(source_data: StreamSourceModel):
    from app.main import stream_worker
    stream_name = source_data.name if source_data.name else "Custom CCTV Stream"
    stream_worker.switch_stream(source_data.url, stream_name)
    # Reset counters on camera switch
    global_state.reset_counters()
    return {
        "status": "success",
        "message": f"Switched stream source to '{stream_name}'",
        "active_source": global_state.get_active_stream()
    }

@router.get("/roi", response_model=ROIModel)
async def get_roi():
    return {
        "inbound": global_state.get_roi("inbound"),
        "outbound": global_state.get_roi("outbound")
    }

@router.post("/roi")
async def update_roi(roi_data: ROIModel):
    global_state.set_roi("inbound", roi_data.inbound)
    global_state.set_roi("outbound", roi_data.outbound)
    return {"status": "success", "message": "ROI updated successfully"}

@router.post("/reset-counter")
async def reset_counter():
    global_state.reset_counters()
    return {"status": "success", "message": "Counters reset successfully"}

@router.get("/stream")
def video_stream():
    return StreamingResponse(
        generate_mjpeg_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
