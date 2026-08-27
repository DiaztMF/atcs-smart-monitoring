@echo off
echo ========================================================
echo   Smart Traffic Monitoring - Start Dev Servers
echo ========================================================
echo.
echo [1/2] Menjalankan Backend FastAPI (Port 8000)...
start "Smart Monitoring - Backend" cmd /k "uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload"
timeout /t 2 >nul

echo [2/2] Menjalankan Frontend Next.js (Port 3000)...
start "Smart Monitoring - Frontend" cmd /k "npm --prefix frontend run dev"

echo.
echo ========================================================
echo   Layanan aktif:
echo   - Frontend: http://localhost:3000
echo   - Backend:  http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo ========================================================
