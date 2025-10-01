@echo off
title Local LLM Interface - Launch
color 0A

echo ========================================
echo   LOCAL LLM INTERFACE
echo ========================================
echo   Gemma 3 27B
echo ========================================
echo.

if not exist "llm_env\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Run install_windows.bat first
    pause
    exit /b 1
)

echo Activating virtual environment...
call llm_env\Scripts\activate.bat

echo.
echo Checking GPU...
python -c "import torch; print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU Mode')"

echo.
echo Starting application...
echo Interface: http://127.0.0.1:7860
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

python app.py

pause
