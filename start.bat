@echo off
echo Starting SceneTalk...

start "Backend" cmd /c "cd backend && uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
start "Frontend" cmd /c "cd frontend && npm run dev"

echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:5500
echo.
echo Both servers are starting. Open http://localhost:5500 when ready.
