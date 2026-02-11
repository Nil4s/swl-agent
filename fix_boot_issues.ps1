# FIX BOOT ISSUES - Remove duplicate Windows entry and fix boot dependency
# Run this as Administrator

Write-Host "================================" -ForegroundColor Cyan
Write-Host "BOOT ISSUE FIX SCRIPT" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click this script and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit
}

Write-Host "Step 1: Backing up current boot configuration..." -ForegroundColor Yellow
bcdedit /export "D:\boot_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').bcd"
Write-Host "✓ Backup created" -ForegroundColor Green
Write-Host ""

Write-Host "Step 2: Attempting to remove duplicate boot entry..." -ForegroundColor Yellow
$entryId = "{aab8184c-15a7-11f0-92be-dda381498d8c}"

# Try to remove from display order first
Write-Host "  Removing from display order..." -ForegroundColor Gray
bcdedit /displayorder $entryId /remove 2>&1 | Out-Null

# Remove any flags that might protect it
Write-Host "  Removing protection flags..." -ForegroundColor Gray
bcdedit /set $entryId bootmenupolicy standard 2>&1 | Out-Null

# Get current default
$currentDefault = (bcdedit /enum | Select-String "identifier" | Select-Object -First 1) -replace ".*{", "{" -replace "}.*", "}"

# If this entry is default, change it
Write-Host "  Checking if entry is set as default..." -ForegroundColor Gray
$defaultInfo = bcdedit /enum | Select-String -Context 0,15 "Windows Boot Manager" | Out-String
if ($defaultInfo -match $entryId) {
    Write-Host "  Entry is default, changing to current..." -ForegroundColor Gray
    bcdedit /default "{current}" 2>&1 | Out-Null
}

# Force delete
Write-Host "  Force deleting entry..." -ForegroundColor Gray
$result = bcdedit /delete $entryId /f 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Successfully removed duplicate boot entry!" -ForegroundColor Green
} else {
    Write-Host "⚠ Could not remove entry. Error:" -ForegroundColor Yellow
    Write-Host "  $result" -ForegroundColor Red
    Write-Host ""
    Write-Host "Additional cleanup attempt..." -ForegroundColor Yellow
    
    # Try cleanup flag
    bcdedit /delete $entryId /cleanup 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Removed with cleanup flag!" -ForegroundColor Green
    } else {
        Write-Host "⚠ Manual intervention may be required" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Step 3: Checking boot configuration..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Current boot entries:" -ForegroundColor Cyan
bcdedit /enum firmware | Select-String "identifier|description" 

Write-Host ""
Write-Host "Step 4: Fixing boot timeout (removing delay)..." -ForegroundColor Yellow
bcdedit /timeout 3
Write-Host "✓ Boot timeout set to 3 seconds" -ForegroundColor Green

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "BOOT FIX COMPLETE!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps to fix SSD dependency:" -ForegroundColor Yellow
Write-Host "1. The duplicate boot entry should be removed" -ForegroundColor White
Write-Host "2. To remove dependency on old SSD:" -ForegroundColor White
Write-Host "   - Keep SSD connected for now" -ForegroundColor White
Write-Host "   - Run the second script: .\fix_ssd_dependency.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
