# FIX SSD BOOT DEPENDENCY
# This script will move the boot partition from the old SSD to your main drive
# Run this as Administrator with BOTH drives connected

Write-Host "================================" -ForegroundColor Cyan
Write-Host "FIX SSD BOOT DEPENDENCY" -ForegroundColor Cyan
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

Write-Host "⚠ IMPORTANT: Make sure BOTH drives are connected!" -ForegroundColor Yellow
Write-Host "   - Main drive (C:)" -ForegroundColor White
Write-Host "   - Old SSD (the one you want to disconnect)" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to continue, or Ctrl+C to abort..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host ""

Write-Host "Step 1: Analyzing disk configuration..." -ForegroundColor Yellow
Write-Host ""

# Show all disks
Get-Disk | Format-Table Number, FriendlyName, Size, PartitionStyle -AutoSize

Write-Host ""
Write-Host "Step 2: Identifying boot partition..." -ForegroundColor Yellow

# Find boot partition (usually small, System partition)
$bootPartition = Get-Partition | Where-Object {$_.Type -eq "System"} | Select-Object -First 1

if ($bootPartition) {
    Write-Host "✓ Boot partition found:" -ForegroundColor Green
    Write-Host "  Disk: $($bootPartition.DiskNumber)" -ForegroundColor White
    Write-Host "  Size: $([math]::Round($bootPartition.Size / 1MB, 0)) MB" -ForegroundColor White
    Write-Host "  Drive Letter: $($bootPartition.DriveLetter)" -ForegroundColor White
    
    $bootDisk = Get-Disk -Number $bootPartition.DiskNumber
    Write-Host "  Located on: $($bootDisk.FriendlyName)" -ForegroundColor White
    Write-Host ""
    
    # Find Windows partition (C:)
    $windowsPartition = Get-Partition | Where-Object {$_.DriveLetter -eq "C"}
    $windowsDisk = Get-Disk -Number $windowsPartition.DiskNumber
    
    Write-Host "Windows installation:" -ForegroundColor Cyan
    Write-Host "  Located on Disk: $($windowsDisk.Number)" -ForegroundColor White
    Write-Host "  Drive: $($windowsDisk.FriendlyName)" -ForegroundColor White
    Write-Host ""
    
    if ($bootPartition.DiskNumber -ne $windowsPartition.DiskNumber) {
        Write-Host "⚠ PROBLEM IDENTIFIED:" -ForegroundColor Red
        Write-Host "  Boot partition is on Disk $($bootPartition.DiskNumber)" -ForegroundColor Yellow
        Write-Host "  Windows is on Disk $($windowsPartition.DiskNumber)" -ForegroundColor Yellow
        Write-Host "  This is why your PC needs both drives!" -ForegroundColor Yellow
        Write-Host ""
        
        Write-Host "Step 3: Rebuilding boot configuration on main drive..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "This will:" -ForegroundColor White
        Write-Host "  1. Rebuild boot files on your main Windows drive (C:)" -ForegroundColor White
        Write-Host "  2. Update boot configuration" -ForegroundColor White
        Write-Host "  3. Make the old SSD optional" -ForegroundColor White
        Write-Host ""
        Write-Host "⚠ This is SAFE but create a backup first if you're worried" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Continue? (Y/N): " -ForegroundColor Cyan -NoNewline
        $response = Read-Host
        
        if ($response -eq "Y" -or $response -eq "y") {
            Write-Host ""
            Write-Host "Backing up boot configuration..." -ForegroundColor Yellow
            bcdedit /export "D:\boot_backup_before_rebuild_$(Get-Date -Format 'yyyyMMdd_HHmmss').bcd"
            Write-Host "✓ Backup created" -ForegroundColor Green
            Write-Host ""
            
            Write-Host "Rebuilding boot configuration on C: drive..." -ForegroundColor Yellow
            
            # Method 1: Use bcdboot to rebuild
            $bcdResult = bcdboot C:\Windows /s C: /f ALL 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Boot files successfully created on C: drive!" -ForegroundColor Green
                Write-Host ""
                Write-Host "Step 4: Updating boot manager..." -ForegroundColor Yellow
                
                # Set Windows Boot Manager to use C: partition
                bcdedit /set "{bootmgr}" device partition=C: 2>&1 | Out-Null
                bcdedit /set "{default}" device partition=C: 2>&1 | Out-Null
                bcdedit /set "{default}" osdevice partition=C: 2>&1 | Out-Null
                
                Write-Host "✓ Boot manager updated!" -ForegroundColor Green
                Write-Host ""
                Write-Host "================================" -ForegroundColor Cyan
                Write-Host "SUCCESS!" -ForegroundColor Green
                Write-Host "================================" -ForegroundColor Cyan
                Write-Host ""
                Write-Host "What to do next:" -ForegroundColor Yellow
                Write-Host "1. Restart your computer (keep old SSD connected)" -ForegroundColor White
                Write-Host "2. If Windows boots normally, shut down" -ForegroundColor White
                Write-Host "3. Disconnect the old SSD" -ForegroundColor White
                Write-Host "4. Boot again - it should work without the old SSD!" -ForegroundColor White
                Write-Host ""
                Write-Host "If something goes wrong:" -ForegroundColor Yellow
                Write-Host "- Reconnect the old SSD" -ForegroundColor White
                Write-Host "- Boot normally" -ForegroundColor White
                Write-Host "- Restore backup: bcdedit /import D:\boot_backup_before_rebuild_*.bcd" -ForegroundColor White
                Write-Host ""
                
            } else {
                Write-Host "⚠ Error during boot rebuild:" -ForegroundColor Red
                Write-Host "$bcdResult" -ForegroundColor Red
                Write-Host ""
                Write-Host "Alternative method: Boot from Windows installation media" -ForegroundColor Yellow
                Write-Host "and use Startup Repair, or contact support" -ForegroundColor Yellow
            }
            
        } else {
            Write-Host "Cancelled by user" -ForegroundColor Yellow
        }
        
    } else {
        Write-Host "✓ Boot partition and Windows are on the same disk!" -ForegroundColor Green
        Write-Host "  Your system should already work without the old SSD" -ForegroundColor White
        Write-Host ""
        Write-Host "The old SSD might be needed for other reasons:" -ForegroundColor Yellow
        Write-Host "- Check if any startup programs reference it" -ForegroundColor White
        Write-Host "- Check BIOS boot order" -ForegroundColor White
    }
    
} else {
    Write-Host "⚠ Could not find boot partition" -ForegroundColor Red
    Write-Host "This might mean:" -ForegroundColor Yellow
    Write-Host "- System uses a hidden partition" -ForegroundColor White
    Write-Host "- Need to check UEFI settings" -ForegroundColor White
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
