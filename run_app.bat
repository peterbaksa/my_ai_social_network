@echo off

:: Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: --- Read conda environment name ---
set "ENV_NAME_FILE=%SCRIPT_DIR%\_conda_env_name"

if not exist "%ENV_NAME_FILE%" (
    echo ERROR: File '%ENV_NAME_FILE%' not found.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

set /p CONDA_ENV_NAME=<"%ENV_NAME_FILE%"
for /f "tokens=* delims= " %%a in ("%CONDA_ENV_NAME%") do set "CONDA_ENV_NAME=%%a"

if "%CONDA_ENV_NAME%"=="" (
    echo ERROR: File '%ENV_NAME_FILE%' is empty or does not contain a valid environment name.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

:: --- Read LLM model name from settings.yaml ---
set "SETTINGS_FILE=%SCRIPT_DIR%\config\settings.yaml"

if not exist "%SETTINGS_FILE%" (
    echo ERROR: File '%SETTINGS_FILE%' not found.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

:: Parse model name from settings.yaml
set "MODEL_NAME="
for /f "tokens=2 delims=: " %%a in ('findstr /r "^.*model:" "%SETTINGS_FILE%"') do (
    if not defined MODEL_NAME (
        set "MODEL_NAME=%%a"
    )
)
:: Remove quotes if present
set "MODEL_NAME=%MODEL_NAME:"=%"
set "MODEL_NAME=%MODEL_NAME:'=%"

if "%MODEL_NAME%"=="" (
    echo ERROR: Could not find model name in '%SETTINGS_FILE%'.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

echo Conda environment: %CONDA_ENV_NAME%
echo LLM model:         %MODEL_NAME%
echo.

:: --- Check if Ollama is available ---
where ollama >nul 2>&1
if errorlevel 1 (
    echo ERROR: Ollama is not installed. Please install it from https://ollama.ai
    echo Press any key to close...
    pause >nul
    exit /b 1
)

:: --- Check if model is downloaded ---
echo Checking if model '%MODEL_NAME%' is available (this may take a moment if Ollama is starting up)...

ollama list | findstr "%MODEL_NAME%" >nul 2>&1
if errorlevel 1 (
    echo Model '%MODEL_NAME%' not found. Downloading (this may take several minutes)...
    echo.
    ollama pull "%MODEL_NAME%"
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to download model '%MODEL_NAME%'.
        echo Press any key to close...
        pause >nul
        exit /b 1
    )
    echo.
    echo Model '%MODEL_NAME%' downloaded successfully.
) else (
    echo Model '%MODEL_NAME%' is already downloaded.
)

echo.

:: --- Check if conda is available ---
where conda >nul 2>&1
if errorlevel 1 (
    echo ERROR: Conda not found. Please make sure conda is installed and in your PATH.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

:: --- Activate the environment ---
echo Activating conda environment '%CONDA_ENV_NAME%'...

call conda activate "%CONDA_ENV_NAME%"
if errorlevel 1 (
    echo ERROR: Failed to activate environment '%CONDA_ENV_NAME%'.
    echo Make sure the environment exists. Run _conda_install_env.bat first.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

echo Environment '%CONDA_ENV_NAME%' activated.
echo.

:: --- Run the application ---
echo Starting AI Social Network...
echo Open http://localhost:8000 in your browser.
echo.

cd /d "%SCRIPT_DIR%"
python -m src.main