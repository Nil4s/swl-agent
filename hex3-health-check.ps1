# Hex3 Health Check Script
# Run every 5 minutes via Windows Task Scheduler

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "[$timestamp] Running Hex3 health check..."

# Check OpenClaw gateway status
$gatewayStatus = openclaw status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Gateway check failed"
} else {
    Write-Host "✅ Gateway status OK"
}

# Check memory usage
$nodeProcesses = Get-Process -Name node -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    $totalMem = ($nodeProcesses | Measure-Object WorkingSet -Sum).Sum / 1MB
    Write-Host "📊 Memory usage: $([math]::Round($totalMem, 2)) MB"
    
    if ($totalMem -gt 1000) {
        Write-Host "⚠️ High memory usage detected"
    }
} else {
    Write-Host "⚠️ No node processes found"
}

# Check disk space
$drive = Get-PSDrive C
$freeGB = [math]::Round($drive.Free / 1GB, 2)
Write-Host "💾 Free disk space: $freeGB GB"

if ($freeGB -lt 10) {
    Write-Host "⚠️ Low disk space warning"
}

# Test API endpoint
try {
    $response = Invoke-RestMethod -Uri "http://localhost:18789/api/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ API endpoint responsive"
} catch {
    Write-Host "⚠️ API endpoint not responding: $_"
}

# Check gateway logs for errors
$logPath = "C:\tmp\openclaw\openclaw-$(Get-Date -Format 'yyyy-MM-dd').log"
if (Test-Path $logPath) {
    $recentErrors = Get-Content $logPath -Tail 50 | Select-String -Pattern "ERROR|WARN"
    if ($recentErrors) {
        Write-Host "⚠️ Recent errors/warnings found:"
        $recentErrors | Select-Object -First 5 | ForEach-Object { Write-Host "  $_" }
    }
}

Write-Host "[$timestamp] Health check complete`n"
