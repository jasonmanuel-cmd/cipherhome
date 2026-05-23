# ============================================================
# CIPHER SOVEREIGN — WINDOWS LAUNCHER (PowerShell)
# Run this from PowerShell as Administrator
# File: cipher_launch.ps1
# ============================================================

Write-Host ""
Write-Host "  ⬡ CIPHER SOVEREIGN v2.0 — INITIALIZING" -ForegroundColor Red
Write-Host "  Where chaos meets clarity." -ForegroundColor DarkGray
Write-Host ""

# ---- CONFIG ----
$CIPHER_DIR    = "$env:USERPROFILE\cipher"
$SERVER_PORT   = 3131
$OLLAMA_PORT   = 11434

# ---- CHECK OLLAMA ----
Write-Host "  [1/5] Checking Ollama..." -ForegroundColor Cyan
$ollamaRunning = $false
try {
    $resp = Invoke-WebRequest -Uri "http://localhost:$OLLAMA_PORT/api/tags" -TimeoutSec 2 -ErrorAction Stop
    $models = ($resp.Content | ConvertFrom-Json).models
    Write-Host "  ✓ Ollama ONLINE — $($models.Count) models loaded" -ForegroundColor Green
    foreach ($m in $models) { Write-Host "    · $($m.name)" -ForegroundColor DarkGray }
    $ollamaRunning = $true
} catch {
    Write-Host "  ⚠ Ollama OFFLINE — starting..." -ForegroundColor Yellow
    Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
    try {
        Invoke-WebRequest -Uri "http://localhost:$OLLAMA_PORT/api/tags" -TimeoutSec 3 -ErrorAction Stop | Out-Null
        Write-Host "  ✓ Ollama started" -ForegroundColor Green
        $ollamaRunning = $true
    } catch {
        Write-Host "  ✗ Ollama failed to start — cloud fallback will be used" -ForegroundColor Red
    }
}

# ---- PULL BEST MODEL IF NONE ----
if ($ollamaRunning) {
    $resp2 = Invoke-WebRequest -Uri "http://localhost:$OLLAMA_PORT/api/tags" -TimeoutSec 2
    $modelList = ($resp2.Content | ConvertFrom-Json).models
    
    if ($modelList.Count -eq 0) {
        Write-Host ""
        Write-Host "  [!] No models found. Pulling DeepSeek R1 8B (fast, sovereign)..." -ForegroundColor Yellow
        Write-Host "  This takes a few minutes on first run." -ForegroundColor DarkGray
        & ollama pull deepseek-r1:8b
    }
    
    # Check for upgrades — pull better model if available bandwidth
    $hasDeepseek = $modelList | Where-Object { $_.name -like "deepseek*" }
    if (-not $hasDeepseek) {
        Write-Host ""
        Write-Host "  [UPGRADE] DeepSeek R1 not found. Pull it for best reasoning? (y/n)" -ForegroundColor Yellow
        $pull = Read-Host "  > "
        if ($pull -eq "y") {
            Write-Host "  Pulling DeepSeek R1:14B — advanced reasoning model..." -ForegroundColor Cyan
            & ollama pull deepseek-r1:14b
        }
    }
}

# ---- SETUP CIPHER DIR ----
Write-Host ""
Write-Host "  [2/5] Setting up Cipher directory..." -ForegroundColor Cyan
if (-not (Test-Path $CIPHER_DIR)) {
    New-Item -ItemType Directory -Path $CIPHER_DIR | Out-Null
}
Write-Host "  ✓ Dir: $CIPHER_DIR" -ForegroundColor Green

# ---- CHECK PYTHON ----
Write-Host ""
Write-Host "  [3/5] Checking Python + dependencies..." -ForegroundColor Cyan
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3") {
            $pythonCmd = $cmd
            Write-Host "  ✓ $ver" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $pythonCmd) {
    Write-Host "  ✗ Python 3 not found." -ForegroundColor Red
    Write-Host "  → Install from: https://python.org/downloads" -ForegroundColor Yellow
    Write-Host "  → Or use WSL2: wsl python3 cipher_server.py" -ForegroundColor Yellow
    exit 1
}

# Install deps
Write-Host "  Installing dependencies..." -ForegroundColor DarkGray
& $pythonCmd -m pip install fastapi uvicorn httpx duckduckgo-search python-dotenv aiohttp -q

# ---- COPY SERVER FILE ----
Write-Host ""
Write-Host "  [4/5] Installing Cipher server..." -ForegroundColor Cyan
$serverSrc = "$PSScriptRoot\cipher_server.py"
$serverDst = "$CIPHER_DIR\cipher_server.py"
if (Test-Path $serverSrc) {
    Copy-Item $serverSrc $serverDst -Force
    Write-Host "  ✓ Server installed to $serverDst" -ForegroundColor Green
} else {
    Write-Host "  ⚠ cipher_server.py not found in same directory as this script" -ForegroundColor Yellow
    Write-Host "  → Place cipher_server.py in: $PSScriptRoot" -ForegroundColor DarkGray
}

# Copy dashboard
$dashSrc = "$PSScriptRoot\cipher_command_center_v2.html"
$dashDst = "$CIPHER_DIR\cipher_command_center_v2.html"
if (Test-Path $dashSrc) {
    Copy-Item $dashSrc $dashDst -Force
    Write-Host "  ✓ Dashboard installed" -ForegroundColor Green
}

# ---- LAUNCH SERVER ----
Write-Host ""
Write-Host "  [5/5] Launching Cipher server on port $SERVER_PORT..." -ForegroundColor Cyan
Write-Host ""
Write-Host "  ┌─────────────────────────────────────────┐" -ForegroundColor Red
Write-Host "  │  CIPHER SOVEREIGN — OPERATIONAL         │" -ForegroundColor Red
Write-Host "  │  Local API:   http://localhost:3131      │" -ForegroundColor Red
Write-Host "  │  Dashboard:   Open cipher_command_center_v2.html  │" -ForegroundColor Red
Write-Host "  │  Status:      http://localhost:3131/status │" -ForegroundColor Red
Write-Host "  └─────────────────────────────────────────┘" -ForegroundColor Red
Write-Host ""

# Open dashboard in browser
$dashPath = $dashDst
if (Test-Path $dashPath) {
    Start-Process $dashPath
}

# Start server
Set-Location $CIPHER_DIR
& $pythonCmd cipher_server.py
