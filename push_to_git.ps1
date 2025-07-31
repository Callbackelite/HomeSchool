# Savage Homeschool OS - Git Push Script
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Savage Homeschool OS - Git Push" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "app.py")) {
    Write-Host "ERROR: app.py not found. Please run this from the SavageHomeschoolOS directory." -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

# Get current timestamp
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Write-Host "Adding all changes to Git..." -ForegroundColor Yellow
git add .

Write-Host ""
Write-Host "Committing changes with timestamp: $timestamp" -ForegroundColor Yellow
git commit -m "Update Savage Homeschool OS - $timestamp"

Write-Host ""
Write-Host "Pushing to remote repository..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "    Push completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Changes have been pushed to:" -ForegroundColor White
Write-Host "https://github.com/Callbackelite/HomeSchool.git" -ForegroundColor Blue
Write-Host ""
Read-Host "Press Enter to continue" 