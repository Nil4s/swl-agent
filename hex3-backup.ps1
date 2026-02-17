# Hex3 Backup Script
# Run daily at 2 AM via Windows Task Scheduler

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupRoot = "D:\backups"
$backupDir = "$backupRoot\hex3_$timestamp"

Write-Host "Starting Hex3 backup to: $backupDir"

# Create backup directory
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

# Backup OpenClaw config and workspace
Write-Host "Backing up OpenClaw configuration..."
Copy-Item -Path "C:\Users\Nick\.openclaw" -Destination "$backupDir\openclaw" -Recurse -Force

# Backup Hex-Warp project
Write-Host "Backing up Hex-Warp project..."
Copy-Item -Path "D:\home\nick\hex3\Hex-Warp" -Destination "$backupDir\Hex-Warp" -Recurse -Force -Exclude ".git","node_modules","*.wav","*.stl"

# Create backup manifest
$manifest = @{
    timestamp = $timestamp
    openclaw_version = (openclaw --version 2>&1 | Out-String)
    git_commit = (git -C "D:\home\nick\hex3\Hex-Warp" rev-parse HEAD 2>&1)
    backup_size_mb = [math]::Round((Get-ChildItem $backupDir -Recurse | Measure-Object Length -Sum).Sum / 1MB, 2)
} | ConvertTo-Json

$manifest | Out-File "$backupDir\manifest.json"

Write-Host "✅ Backup complete"
Write-Host "Location: $backupDir"
Write-Host "Size: $($manifest | ConvertFrom-Json | Select-Object -ExpandProperty backup_size_mb) MB"

# Cleanup old backups (keep last 7 days)
Write-Host "Cleaning up old backups..."
$oldBackups = Get-ChildItem $backupRoot -Directory | 
    Where-Object { $_.Name -match "hex3_\d{8}" } |
    Sort-Object Name |
    Select-Object -SkipLast 7

if ($oldBackups) {
    $oldBackups | ForEach-Object {
        Write-Host "Removing old backup: $($_.Name)"
        Remove-Item $_.FullName -Recurse -Force
    }
}

Write-Host "Backup complete!"
