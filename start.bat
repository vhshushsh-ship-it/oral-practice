@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ═══════════════════════════════════════════════
echo   SceneTalk — 一键启动
echo ═══════════════════════════════════════════════
echo.

set MYSQL_DIR=C:\Program Files\MySQL\MySQL Server 8.4
set MYSQL_CONF=C:\ProgramData\MySQL\MySQL Server 8.4\my.ini

:: ── 1. MySQL ──
echo [1/3] 检查 MySQL 服务...
netstat -an 2>nul | find ":3306" | find "LISTENING" >nul
if %errorlevel%==0 (
    echo   MySQL 已在运行 (端口 3306)
) else (
    echo   正在启动 MySQL...
    start "MySQL" /MIN "%MYSQL_DIR%\bin\mysqld.exe" --defaults-file="%MYSQL_CONF%" --console
    echo   等待 MySQL 就绪...
    for /L %%i in (1,1,20) do (
        timeout /t 1 >nul
        netstat -an 2>nul | find ":3306" | find "LISTENING" >nul
        if !errorlevel!==0 goto mysql_ready
        echo | set /p="."
    )
    echo    MySQL 启动超时，请手动检查
    pause
    exit /b 1
)
:mysql_ready
echo   MySQL ✓
echo.

:: ── 2. Backend ──
echo [2/3] 启动后端 (FastAPI :8000)...
start "Backend" cmd /c "cd /d "%~dp0backend" && uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
echo   等待后端就绪...
for /L %%i in (1,1,15) do (
    timeout /t 1 >nul
    curl -s http://127.0.0.1:8000/api/listening/sets 2>nul | find "sets" >nul
    if !errorlevel!==0 goto backend_ready
    echo | set /p="."
)
echo   后端启动超时，请检查 backend 目录
pause
exit /b 1
:backend_ready
echo   后端 ✓
echo.

:: ── 3. Frontend ──
echo [3/3] 启动前端 (Vite :5500)...
start "Frontend" cmd /c "cd /d "%~dp0frontend" && npm run dev"
echo   等待前端就绪...
for /L %%i in (1,1,15) do (
    timeout /t 1 >nul
    curl -s http://127.0.0.1:5500 2>nul | find "html" >nul
    if !errorlevel!==0 goto frontend_ready
    echo | set /p="."
)
echo   前端启动超时，请检查 frontend 目录
pause
exit /b 1
:frontend_ready
echo   前端 ✓

echo.
echo ═══════════════════════════════════════════════
echo   全部启动完成！
echo   后端:   http://127.0.0.1:8000
echo   前端:   http://localhost:5500
echo ═══════════════════════════════════════════════
echo.
echo 按任意键打开浏览器...
pause >nul
start http://localhost:5500
echo.
echo 关闭此窗口不会停止服务。请手动关闭 MySQL/Backend/Frontend 窗口。
echo.
pause
