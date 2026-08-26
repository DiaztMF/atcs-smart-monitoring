import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.state import global_state

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"

def test_roi_get_and_post_valid():
    new_roi = {
        "inbound": [[0.1, 0.2], [0.3, 0.2], [0.3, 0.8], [0.1, 0.8]],
        "outbound": [[0.6, 0.2], [0.8, 0.2], [0.8, 0.8], [0.6, 0.8]]
    }
    post_res = client.post("/api/v1/roi", json=new_roi)
    assert post_res.status_code == 200
    
    get_res = client.get("/api/v1/roi")
    assert get_res.status_code == 200
    res_data = get_res.json()
    assert res_data["inbound"] == new_roi["inbound"]
    assert res_data["outbound"] == new_roi["outbound"]

def test_roi_post_validation_error_fewer_than_3_points():
    # Attempt to post a polygon with only 2 points (invalid contour)
    invalid_roi = {
        "inbound": [[0.1, 0.2], [0.3, 0.2]],
        "outbound": []
    }
    post_res = client.post("/api/v1/roi", json=invalid_roi)
    assert post_res.status_code == 422 # Unprocessable Entity validation error

def test_roi_post_validation_error_out_of_bounds():
    # Attempt to post a point with coordinate > 1.0
    invalid_roi = {
        "inbound": [[0.1, 0.2], [0.3, 0.2], [1.5, 0.8]],
        "outbound": []
    }
    post_res = client.post("/api/v1/roi", json=invalid_roi)
    assert post_res.status_code == 422

def test_reset_counter():
    res = client.post("/api/v1/reset-counter")
    assert res.status_code == 200
    metrics = global_state.get_metrics()
    assert metrics["inbound"]["total_smp"] == 0.0
