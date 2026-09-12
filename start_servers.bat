@echo off
echo ========================================================
echo Starting Freight Intelligence Platform...
echo ========================================================

set "NODE_DIR=C:\Users\Dev\AppData\Local\Microsoft\WinGet\Packages\OpenJS.NodeJS.LTS_Microsoft.Winget.Source_8wekyb3d8bbwe\node-v24.19.0-win-x64"
set "PATH=%NODE_DIR%;%PATH%"

echo 1. Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "Freight Backend (FastAPI)" cmd /k "python -c ""import uvicorn; from app.demo_server import app; uvicorn.run(app, host='127.0.0.1', port=8000)"""

timeout /t 3 /nobreak >nul

echo 2. Starting React/Vite Frontend on http://127.0.0.1:5173 ...
start "Freight Frontend (Vite)" cmd /k "cd frontend && npm run dev -- --host 127.0.0.1 --port 5173"

timeout /t 3 /nobreak >nul

echo ========================================================
echo App is ready!
echo Open your browser at: http://127.0.0.1:5173
echo API documentation:    http://127.0.0.1:8000/docs
echo ========================================================
