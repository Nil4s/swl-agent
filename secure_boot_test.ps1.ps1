# SECURE BOOT TO CURRENT OS
# This will rebuild boot on C: and let you test if old SSD is still needed

Write-Host "================================" -ForegroundColor Cyan
Write-Host "SECURE BOOT & TEST SSD" -ForegroundColor Cyan  
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Must run as admin
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Please run as Administrator!" -ForegroundColor Red
    pause
    exit
}

Write-Host "Step 1: Creating backup..." -ForegroundColor Yellow
bcdedit /export "D:\boot_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').bcd"
Write-Host "✓ Backup saved to D:\" -ForegroundColor Green
Write-Host ""

Write-Host "Step 2: Rebuilding boot on C: drive..." -ForegroundColor Yellow
Write-Host "This will make C: drive bootable independently" -ForegroundColor White
Write-Host ""

# Rebuild boot files on C:
bcdboot C:\Windows /s C: /f ALL

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Boot files rebuilt on C:" -ForegroundColor Green
} else {
    Write-Host "⚠ There was an issue" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 3: Setting boot priority..." -ForegroundColor Yellow

# Make sure default boot points to C:
bcdedit /set "{bootmgr}" device partition=C:
bcdedit /set "{default}" device partition=C:
bcdedit /set "{default}" osdevice partition=C:

Write-Host "✓ Boot priority set to C: drive" -ForegroundColor Green
Write-Host ""

Write-Host "Step 4: Hiding boot menu..." -ForegroundColor Yellow
bcdedit /timeout 1
bcdedit /set "{bootmgr}" displaybootmenu no

Write-Host "✓ Boot menu hidden (1 second timeout)" -ForegroundColor Green
Write-Host ""

Write-Host "================================" -ForegroundColor Cyan
Write-Host "READY TO TEST!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart your computer NOW (with old SSD still connected)" -ForegroundColor White
Write-Host "2. Make sure Windows boots normally" -ForegroundColor White
Write-Host "3. Shut down completely" -ForegroundColor White
Write-Host "4. Disconnect the old SSD" -ForegroundColor White
Write-Host "5. Try to boot" -ForegroundColor White
Write-Host ""
Write-Host "If it WORKS without old SSD:" -ForegroundColor Green
Write-Host "  ✓ You're done! Old SSD is now optional" -ForegroundColor White
Write-Host ""
Write-Host "If it FAILS without old SSD:" -ForegroundColor Red
Write-Host "  - Reconnect old SSD" -ForegroundColor White
Write-Host "  - Boot normally" -ForegroundColor White
Write-Host "  - The boot partition is still on old SSD" -ForegroundColor White
Write-Host "  - You'll need to clone it or keep SSD connected" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to close and restart..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
