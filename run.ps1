# DRDO SIH26055 Electronic Warfare Smart Scan - One-Click Launcher
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " AURA-ES: Smart Scan Strategy for Electronic Warfare (SIH26055)" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Start FastAPI Backend in background
Write-Host "`n[1/2] Starting FastAPI backend on http://127.0.0.1:8000..." -ForegroundColor Green
$backendProcess = Start-Process -FilePath "python" -ArgumentList "-m uvicorn api.main:app --host 127.0.0.1 --port 8000" -PassThru -NoNewWindow

Start-Sleep -Seconds 2

# 2. Start Vite Frontend in background
Write-Host "[2/2] Starting Vite Frontend on http://127.0.0.1:5173..." -ForegroundColor Green
Set-Location -Path "web"
$frontendProcess = Start-Process -FilePath "npm" -ArgumentList "run dev -- --host 127.0.0.1 --port 5173" -PassThru -NoNewWindow
Set-Location -Path ".."

Write-Host "`nAll services active!" -ForegroundColor Cyan
Write-Host "Dashboard: http://127.0.0.1:5173 (or assigned port)" -ForegroundColor Yellow
Write-Host "Backend API: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "Swagger Docs: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "`nPress Ctrl+C to terminate all services." -ForegroundColor Gray

try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
finally {
    Write-Host "`nShutting down services..." -ForegroundColor Red
    Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
}
