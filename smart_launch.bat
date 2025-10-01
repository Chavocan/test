@echo off
title Local LLM Interface - Smart Launch
color 0A

echo.
echo ========================================
echo   LOCAL LLM INTERFACE - SMART LAUNCH
echo ========================================
echo   Gemma 3 27B with Auto Health Check
echo ========================================
echo.

:: Check if virtual environment exists
if not exist "llm_env\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run install_windows.bat first
    echo.
    pause
    exit /b 1
)

:: Activate virtual environment
echo [1/4] Activating virtual environment...
call llm_env\Scripts\activate.bat

:: Run health check
echo.
echo [2/4] Running system health check...
echo ----------------------------------------
python startup_check.py
set HEALTH_CHECK_RESULT=%ERRORLEVEL%

echo.
echo ----------------------------------------

if %HEALTH_CHECK_RESULT% NEQ 0 (
    echo.
    echo WARNING: Health check found issues!
    echo.
    echo You can either:
    echo   1. Fix the issues and try again
    echo   2. Continue anyway ^(may not work properly^)
    echo.
    set /p CONTINUE="Continue anyway? (y/n): "
    
    if /i not "%CONTINUE%"=="y" (
        echo.
        echo Launch cancelled. Please fix the issues and try again.
        pause
        exit /b 1
    )
)

:: Close GPU-heavy applications reminder
echo.
echo [3/4] Pre-launch checks...
echo ----------------------------------------
echo TIP: For best performance, close these if running:
echo   - Chrome/Edge browsers
echo   - Discord
echo   - OBS/Streaming software
echo   - Other AI applications
echo.

:: Check GPU
python -c "import torch; gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU Mode'; print(f'GPU: {gpu}')" 2>nul
if errorlevel 1 (
    echo WARNING: Could not detect GPU
    echo Will run in CPU mode ^(slower^)
    echo.
)

echo ----------------------------------------
echo.

:: Final confirmation
set /p START="Ready to start application? (y/n): "
if /i not "%START%"=="y" (
    echo.
    echo Launch cancelled.
    pause
    exit /b 0
)

:: Launch application
echo.
echo [4/4] Starting Local LLM Interface...
echo ========================================
echo.
echo Model: Gemma-3-27b-it-abliterated
echo Interface: http://127.0.0.1:7860
echo.
echo The browser should open automatically.
echo If not, manually open: http://127.0.0.1:7860
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

:: Start the application
python app.py

:: If app exits, show message
echo.
echo ========================================
echo Application stopped
echo ========================================
echo.
pause