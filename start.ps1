# SceneTalk One-Click Startup Script
# Launched by start.bat — double-click start.bat to run

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$LogFile = Join-Path $ScriptDir "startup.log"
$LogLines = @()

function Write-Status($msg) {
    $timestamp = Get-Date -Format "HH:mm:ss"
    $line = "[$timestamp] $msg"
    $LogLines += $line
    Write-Host $line
}

function Save-Log {
    $LogLines | Out-File -FilePath $LogFile -Encoding UTF8
}

# ── Config ────────────────────────────────────────────
$MySQLDir  = "C:\Program Files\MySQL\MySQL Server 8.4"
$MySQLConf = "C:\ProgramData\MySQL\MySQL Server 8.4\my.ini"
$BackendPort  = 8000
$FrontendPort = 5500
$MySQLPort    = 3306

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SceneTalk - One Click Start" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Status "Starting SceneTalk..."

# ── Helper: Get PID listening on a port ────────────────
function Get-PidOnPort($port) {
    $result = netstat -ano 2>$null | Select-String ":$port\b" | Select-String "LISTENING"
    if ($result) {
        $line = $result -replace '\s+', ' ' | ForEach-Object { $_.Trim() }
        $parts = $line -split ' '
        $procId = $parts[-1]
        if ($procId -match '^\d+$') {
            return [int]$procId
        }
    }
    return $null
}

# ── Helper: Check if port is listening ─────────────────
function Test-Port($port) {
    $result = netstat -an 2>$null | Select-String ":$port\b" | Select-String "LISTENING"
    return ($null -ne $result)
}

# ── Helper: Kill process by port ──────────────────────
function Kill-Port($port, $label) {
    $procId = Get-PidOnPort $port
    if ($procId) {
        try {
            Stop-Process -Id $procId -Force -ErrorAction Stop
            Write-Status "Killed old $label (PID: $procId, Port: $port)"
        } catch {
            Write-Status "WARNING: Could not kill $label (PID: $procId)"
        }
    }
}

# ── Helper: Wait for HTTP endpoint ────────────────────
function Wait-Http($url, $pattern, $label, $timeoutSec = 60) {
    $elapsed = 0
    $interval = 2
    while ($elapsed -lt $timeoutSec) {
        try {
            $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 3
            if ($pattern) {
                if ($response.Content -match $pattern) {
                    Write-Status "$label ready!"
                    return $true
                }
            } elseif ($response.StatusCode -eq 200) {
                Write-Status "$label ready!"
                return $true
            }
        } catch {
            # Still waiting...
        }
        Write-Host -NoNewline "."
        Start-Sleep -Seconds $interval
        $elapsed += $interval
    }
    Write-Host ""
    return $false
}

# ══════════════════════════════════════════════════════
# Step 0: Kill old processes
# ══════════════════════════════════════════════════════
Write-Status "[0/3] Cleaning old processes..."
Kill-Port $BackendPort "backend"
Kill-Port $FrontendPort "frontend"

# ══════════════════════════════════════════════════════
# Step 1: MySQL
# ══════════════════════════════════════════════════════
Write-Status "[1/3] MySQL database (port $MySQLPort)..."

if (Test-Port $MySQLPort) {
    Write-Status "MySQL already running."
} else {
    $mysqld = Join-Path $MySQLDir "bin\mysqld.exe"
    if (-not (Test-Path $mysqld)) {
        Write-Status "ERROR: MySQL not found at $mysqld"
        Write-Status "Please edit `$MySQLDir in start.ps1"
        Write-Host ""
        Save-Log
        Read-Host "Press Enter to exit"
        exit 1
    }

    Write-Status "Starting MySQL..."
    if (Test-Path $MySQLConf) {
        $mysqlArgs = @("--defaults-file=`"$MySQLConf`"", "--console")
    } else {
        $mysqlArgs = @("--console")
    }
    Start-Process -FilePath $mysqld -ArgumentList $mysqlArgs -WindowStyle Minimized

    Write-Status "Waiting for MySQL..."
    $elapsed = 0
    while ($elapsed -lt 60) {
        Start-Sleep -Seconds 2
        $elapsed += 2
        if (Test-Port $MySQLPort) {
            Write-Status "MySQL ready!"
            break
        }
        Write-Host -NoNewline "."
    }
    Write-Host ""
    if (-not (Test-Port $MySQLPort)) {
        Write-Status "ERROR: MySQL startup timeout."
        Save-Log
        Read-Host "Press Enter to exit"
        exit 1
    }
}
Write-Status "MySQL OK."

# ══════════════════════════════════════════════════════
# Step 2: Backend
# ══════════════════════════════════════════════════════
Write-Status "[2/3] Backend (FastAPI, port $BackendPort)..."

python -c "import fastapi,uvicorn,aiomysql" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Status "Installing Python dependencies..."
    $reqFile = Join-Path $ScriptDir "backend\requirements.txt"
    pip install -r $reqFile -q 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Status "ERROR: pip install failed."
        Save-Log
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Status "Starting backend..."
$backendDir = Join-Path $ScriptDir "backend"
$backendCmd = "cd /d $backendDir && uvicorn main:app --host 127.0.0.1 --port $BackendPort --reload"
Start-Process cmd -ArgumentList "/c", $backendCmd -WindowStyle Normal

$ready = Wait-Http "http://127.0.0.1:$BackendPort/api/listening/sets" "sets" "Backend" 60
if (-not $ready) {
    Write-Status "ERROR: Backend startup timeout."
    Write-Status "Check: backend\.env, MySQL, port $BackendPort"
    Save-Log
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Status "Backend OK."

# ══════════════════════════════════════════════════════
# Step 3: Frontend
# ══════════════════════════════════════════════════════
Write-Status "[3/3] Frontend (Vite, port $FrontendPort)..."

$frontendDir = Join-Path $ScriptDir "frontend"
if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    Write-Status "Installing npm dependencies..."
    Push-Location $frontendDir
    $null = npm install 2>&1
    Pop-Location
    if ($LASTEXITCODE -ne 0) {
        Write-Status "ERROR: npm install failed."
        Save-Log
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Status "Starting frontend..."
$frontendCmd = "cd /d $frontendDir && npm run dev"
Start-Process cmd -ArgumentList "/c", $frontendCmd -WindowStyle Normal

$ready = Wait-Http "http://127.0.0.1:$FrontendPort" $null "Frontend" 60
if (-not $ready) {
    Write-Status "Frontend may still be compiling. Continuing anyway..."
} else {
    Write-Status "Frontend OK."
}

# ══════════════════════════════════════════════════════
# Done
# ══════════════════════════════════════════════════════
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  All services started!" -ForegroundColor Green
Write-Host "  Backend:  http://127.0.0.1:$BackendPort" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:$FrontendPort" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

Write-Status "Opening browser..."
Start-Process "http://localhost:$FrontendPort"

Write-Host ""
Write-Host "Services run in separate windows."
Write-Host "Close this window when done with all services."
Write-Host ""

Save-Log
Read-Host "Press Enter to exit"
