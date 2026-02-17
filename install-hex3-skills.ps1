# Hex3 Skills Installation Script
# Install essential skills for Hex3 workflow

Write-Host "🦞 Installing Hex3 Essential Skills" -ForegroundColor Cyan
Write-Host ""

# Note: OpenClaw 2026.2.9+ has bundled skills
# Skills are auto-discovered, no npm install needed

# List currently available skills
Write-Host "Checking available skills..." -ForegroundColor Yellow
openclaw skills

Write-Host ""
Write-Host "✅ Skills check complete" -ForegroundColor Green
Write-Host ""
Write-Host "Available bundled skills include:" -ForegroundColor Cyan
Write-Host "  • coding-agent - AI code generation and analysis"
Write-Host "  • gemini - Google Gemini API integration"
Write-Host "  • healthcheck - System health monitoring"
Write-Host "  • skill-creator - Create custom skills"
Write-Host "  • github - GitHub API integration (if available)"
Write-Host ""
Write-Host "To enable a skill, add it to openclaw.json or use:" -ForegroundColor Yellow
Write-Host '  openclaw config set agents.defaults.skills ''["skill-name"]'''
Write-Host ""
Write-Host "For custom skills, place in:" -ForegroundColor Yellow
Write-Host "  C:\Users\Nick\.openclaw\skills\"
Write-Host ""
