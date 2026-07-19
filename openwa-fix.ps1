# OpenWA Troubleshooting Script
# Run in PowerShell as Administrator

Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  OpenWA Setup Fixer v1.0" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Check Node.js
Write-Host "[1/5] Checking Node.js..." -ForegroundColor Yellow
node --version
npm --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Node.js not found! Install from: https://nodejs.org" -ForegroundColor Red
    Write-Host "   Download LTS version (v22.x)" -ForegroundColor Gray
    exit 1
}
Write-Host "✅ Node.js OK" -ForegroundColor Green

# Check ports
Write-Host ""
Write-Host "[2/5] Checking Port 2785..." -ForegroundColor Yellow
$portCheck = netstat -ano | Select-String ":2785"
if ($portCheck) {
    Write-Host "⚠️ Port 2785 is in use!" -ForegroundColor Red
    Write-Host "   Run this to find and kill the process:" -ForegroundColor Gray
    Write-Host "   netstat -ano | Select-String ':2785'" -ForegroundColor Gray
    Write-Host "   taskkill /PID <PID> /F" -ForegroundColor Gray
} else {
    Write-Host "✅ Port 2785 is free" -ForegroundColor Green
}

# Check OpenWA folder
Write-Host ""
Write-Host "[3/5] Checking OpenWA folder..." -ForegroundColor Yellow
if (Test-Path "C:\OpenWA") {
    Write-Host "✅ OpenWA folder found at C:\OpenWA" -ForegroundColor Green
    Set-Location "C:\OpenWA"
} elseif (Test-Path "C:\Users\PC\OpenWA") {
    Write-Host "✅ OpenWA folder found" -ForegroundColor Green
    Set-Location "C:\Users\PC\OpenWA"
} else {
    Write-Host "⚠️ OpenWA not cloned yet" -ForegroundColor Red
    Write-Host "   Run:" -ForegroundColor Gray
    Write-Host "   cd C:\" -ForegroundColor Gray
    Write-Host "   git clone https://github.com/rmyndharis/OpenWA.git" -ForegroundColor Gray
}

# Fix npm issues
Write-Host ""
Write-Host "[4/5] If npm install failed, trying to fix..." -ForegroundColor Yellow
if (Test-Path "C:\OpenWA\package.json") {
    Set-Location "C:\OpenWA"
    Write-Host "   Clearing npm cache..." -ForegroundColor Gray
    npm cache clean --force
    Write-Host "   Removing node_modules..." -ForegroundColor Gray
    Remove-Item -Recurse -Force "node_modules" -ErrorAction SilentlyContinue
    Write-Host "   Removing package-lock.json..." -ForegroundColor Gray
    Remove-Item -Force "package-lock.json" -ErrorAction SilentlyContinue
    Write-Host "   Run 'npm install' again after this script" -ForegroundColor Gray
}

# Docker check
Write-Host ""
Write-Host "[5/5] Docker Check..." -ForegroundColor Yellow
docker --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Docker not installed. Option:" -ForegroundColor Red
    Write-Host "   1. Install Docker from https://docker.com" -ForegroundColor Gray
    Write-Host "   2. Or use npm method without Docker" -ForegroundColor Gray
} else {
    Write-Host "✅ Docker installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Quick Start Options:" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "OPTION A - Docker (Recommended):" -ForegroundColor Yellow
Write-Host "  cd C:\OpenWA" -ForegroundColor Gray
Write-Host "  docker compose -f docker-compose.dev.yml up -d" -ForegroundColor Gray
Write-Host ""
Write-Host "OPTION B - NPM (if Docker fails):" -ForegroundColor Yellow
Write-Host "  cd C:\OpenWA" -ForegroundColor Gray
Write-Host "  npm install" -ForegroundColor Gray
Write-Host "  npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "Access OpenWA at:" -ForegroundColor Cyan
Write-Host "  Dashboard: http://localhost:2785" -ForegroundColor White
Write-Host "  API Docs:  http://localhost:2785/api/docs" -ForegroundColor White
Write-Host ""
