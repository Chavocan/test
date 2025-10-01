@echo off
title Local LLM Interface - Gemma 3 27B

echo ========================================
echo Starting Local LLM Interface
echo ========================================
echo.

:: Activate virtual environment
call llm_env\Scripts\activate.bat

:: Check if CUDA is available
echo Checking GPU...
python -c "import torch; print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU Mode')"
echo.

:: Launch the application
echo.
echo Starting application...
echo Interface will be available at: http://127.0.0.1:7860
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python app.py

pause