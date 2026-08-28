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
    assert "active_stream" in data

def test_stream_source_endpoints():
    get_res = client.get("/api/v1/stream-source")
    assert get_res.status_code == 200
    data = get_res.json()
    assert "active_source" in data
    assert "presets" in data
    assert len(data["presets"]) >= 4

    # Test switching stream source
    post_res = client.post("/api/v1/stream-source", json={
        "url": "http://example.com/cctv_test.flv",
        "name": "Test CCTV Cam 1"
    })
    assert post_res.status_code == 200
    post_data = post_res.json()
    assert post_data["status"] == "success"
    assert global_state.get_active_stream()["name"] == "Test CCTV Cam 1"

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
    invalid_roi = {
        "inbound": [[0.1, 0.2], [0.3, 0.2]],
        "outbound": []
    }
    post_res = client.post("/api/v1/roi", json=invalid_roi)
    assert post_res.status_code == 422

def test_roi_post_validation_error_out_of_bounds():
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

def test_cors_preflight_and_vercel_origin():
    # Test preflight OPTIONS request from a Vercel deployment domain
    headers = {
        "Origin": "https://atcs-smart-monitoring-frontend.vercel.app",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    }
    options_res = client.options("/api/v1/roi", headers=headers)
    assert options_res.status_code == 200
    assert options_res.headers.get("access-control-allow-origin") == "*"
    assert "POST" in options_res.headers.get("access-control-allow-methods", "")

    # Test GET /api/v1/roi from Vercel origin
    get_roi_res = client.get("/api/v1/roi", headers={"Origin": "https://atcs-smart-monitoring-frontend.vercel.app"})
    assert get_roi_res.status_code == 200
    assert get_roi_res.headers.get("access-control-allow-origin") == "*"

    # Test GET /api/v1/stream-source from Vercel origin
    get_src_res = client.get("/api/v1/stream-source", headers={"Origin": "https://atcs-smart-monitoring-frontend.vercel.app"})
    assert get_src_res.status_code == 200
    assert get_src_res.headers.get("access-control-allow-origin") == "*"
