@echo off
echo.
echo ========================================
echo    Savage Homeschool OS - Git Push
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "app.py" (
    echo ERROR: app.py not found. Please run this from the SavageHomeschoolOS directory.
    pause
    exit /b 1
)

REM Get current timestamp for commit message
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%-%MM%-%DD% %HH%:%Min%:%Sec%"

echo Adding all changes to Git...
git add .

echo.
echo Committing changes with timestamp: %timestamp%
git commit -m "Update Savage Homeschool OS - %timestamp%"

echo.
echo Pushing to remote repository...
git push origin main

echo.
echo ========================================
echo    Push completed successfully!
echo ========================================
echo.
echo Changes have been pushed to:
echo https://github.com/Callbackelite/HomeSchool.git
echo.
pause 