---
title: ATCS Smart Monitoring Backend
emoji: 🚦
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 5.16.0
app_file: app.py
pinned: false
---

# ATCS Smart Traffic Monitoring — Backend Service

Real-Time Computer Vision & Traffic Analytics Backend powered by FastAPI, YOLOv11 Nano, ByteTrack, and Gradio 5.

## Endpoints

- **Live Stream (MJPEG):** `/api/v1/stream`
- **ROI Config (GET/POST):** `/api/v1/roi`
- **Health Check:** `/api/v1/health`
- **Counter Reset:** `/api/v1/reset-counter`
- **WebSocket Broadcaster:** `/ws/metrics`
