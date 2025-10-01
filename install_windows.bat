@echo off
echo ========================================
echo Local LLM Interface Installation
echo Optimized for RTX 4080 + Ryzen 7 7800X3D
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from python.org
    pause
    exit /b 1
)

echo [1/6] Creating virtual environment...
python -m venv llm_env
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/6] Activating virtual environment...
call llm_env\Scripts\activate.bat

echo [3/6] Upgrading pip...
python -m pip install --upgrade pip

echo [4/6] Installing PyTorch with CUDA 11.8 support...
echo This will take several minutes...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo [5/6] Installing core dependencies...
pip install transformers>=4.35.0
pip install accelerate>=0.24.0
pip install bitsandbytes>=0.41.0
pip install optimum>=1.14.0
pip install gradio>=4.0.0
pip install sentencepiece>=0.1.99

echo [6/6] Installing audio and utility packages...
:: Better audio - NO PIPER!
pip install edge-tts>=6.1.9
pip install SpeechRecognition>=3.10.0
pip install faster-whisper>=0.9.0

:: Try to install pyaudio (can be tricky on Windows)
echo Installing PyAudio for microphone support...
pip install pyaudio
if errorlevel 1 (
    echo.
    echo WARNING: PyAudio installation failed.
    echo You can install it manually from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
    echo Or skip microphone input for now
    echo.
)

:: Install optional high-quality TTS
echo.
echo Do you want to install Coqui TTS? (Very high quality but slower)
echo This is optional - Edge TTS is already installed and sounds great.
set /p install_coqui="Install Coqui TTS? (y/n): "
if /i "%install_coqui%"=="y" (
    pip install TTS>=0.22.0
)

:: Other utilities
pip install pillow>=10.0.0
pip install pyautogui>=0.9.54
pip install requests>=2.31.0
pip install beautifulsoup4>=4.12.0
pip install duckduckgo-search>=3.9.0
pip install python-dotenv>=1.0.0
pip install pyyaml>=6.0

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Creating project directories...
mkdir chat_histories 2>nul
mkdir context_files 2>nul
mkdir context_files\personal 2>nul
mkdir context_files\projects 2>nul
mkdir context_files\learning 2>nul
mkdir context_files\reference 2>nul
mkdir context_files\auto_generated 2>nul
mkdir uploads 2>nul
mkdir downloads 2>nul
mkdir model_offload 2>nul
mkdir logs 2>nul
mkdir .cache 2>nul
mkdir temp 2>nul

echo.
echo ========================================
echo Testing CUDA availability...
echo ========================================
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"

echo.
echo ========================================
echo Setup Information
echo ========================================
echo.
echo Virtual Environment: llm_env
echo To activate: llm_env\Scripts\activate.bat
echo To run app: python app.py
echo.
echo Optimized for your system:
echo - RTX 4080 (16GB) with 4-bit quantization
echo - 16K context window for maximum memory
echo - High-quality Edge TTS (Microsoft voices)
echo - Faster-Whisper for speech recognition
echo - Auto-context management at 90%%
echo.
echo Next steps:
echo 1. Ensure all files (app.py, config.py, etc.) are in this directory
echo 2. Review system_config.yaml for any custom settings
echo 3. Run: launch.bat
echo 4. Open browser to: http://127.0.0.1:7860
echo.
echo First run will download the model (~54GB) - this takes time!
echo.
echo ========================================
pause
