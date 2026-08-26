---
title: ATCS Smart Monitoring Backend
emoji: 🚦
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
---

# ATCS Smart Traffic Monitoring — Backend Service

Real-Time Computer Vision & Traffic Analytics Backend powered by FastAPI, YOLOv11 Nano, and ByteTrack.

## Endpoints

- **Live Stream (MJPEG):** `/api/v1/stream`
- **ROI Config (GET/POST):** `/api/v1/roi`
- **Health Check:** `/api/v1/health`
- **Counter Reset:** `/api/v1/reset-counter`
- **WebSocket Broadcaster:** `/ws/metrics`
