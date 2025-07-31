@echo off
title Savage Homeschool OS
color 0A

echo.
echo ========================================
echo    Savage Homeschool OS Launcher
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo Python found! Starting Savage Homeschool OS...
echo.

python run.py

echo.
echo Savage Homeschool OS has stopped.
pause 