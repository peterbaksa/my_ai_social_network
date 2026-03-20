#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# --- Read conda environment name ---
ENV_NAME_FILE="$SCRIPT_DIR/_conda_env_name"

if [ ! -f "$ENV_NAME_FILE" ]; then
    echo "ERROR: File '$ENV_NAME_FILE' not found."
    echo "Press any key to close..."
    read -n 1 -s
    exit 1
fi

CONDA_ENV_NAME="$(cat "$ENV_NAME_FILE" | tr -d '[:space:]')"

if [ -z "$CONDA_ENV_NAME" ]; then
    echo "ERROR: File '$ENV_NAME_FILE' is empty or does not contain a valid environment name."
    echo "Press any key to close..."
    read -n 1 -s
    exit 1
fi

# --- Read LLM model name from settings.yaml ---
SETTINGS_FILE="$SCRIPT_DIR/config/settings.yaml"

if [ ! -f "$SETTINGS_FILE" ]; then
    echo "ERROR: File '$SETTINGS_FILE' not found."
    echo "Press any key to close..."
    read -n 1 -s
    exit 1
fi

MODEL_NAME="$(grep 'model:' "$SETTINGS_FILE" | head -1 | sed 's/.*model:[[:space:]]*//' | tr -d '\"' | tr -d "'" | tr -d '[:space:]')"

if [ -z "$MODEL_NAME" ]; then
    echo "ERROR: Could not find model name in '$SETTINGS_FILE'."
    echo "Press any key to close..."
    read -n 1 -s
    exit 1
fi

echo "Conda environment: $CONDA_ENV_NAME"
echo "LLM model:         $MODEL_NAME"
echo ""

# --- Check if Ollama is running ---
if ! command -v ollama &> /dev/null; then
    echo "ERROR: Ollama is not installed. Please install it from https://ollama.ai"
    echo "Press any key to close..."
    read -n 1 -s
    exit 1
fi

# --- Check if model is downloaded ---
echo "Checking if model '$MODEL_NAME' is available..."

if ollama list | grep -q "$MODEL_NAME"; then
    echo "Model '$MODEL_NAME' is already downloaded."
else
    echo "Model '$MODEL_NAME' not found. Downloading..."
    echo ""
    if ollama pull "$MODEL_NAME"; then
        echo ""
        echo "Model '$MODEL_NAME' downloaded successfully."
    else
        echo ""
        echo "ERROR: Failed to download model '$MODEL_NAME'."
        echo "Press any key to close..."
        read -n 1 -s
        exit 1
    fi
fi

echo ""

# --- Initialize conda for this shell session ---
if [ -f "$HOME/miniforge3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniforge3/etc/profile.d/conda.sh"
elif [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/anaconda3/etc/profile.d/conda.sh"
elif command -v conda &> /dev/null; then
    eval "$(conda shell.bash hook)"
else
    echo "ERROR: Conda not found. Please make sure conda is installed."
    echo "Press any key to close..."
    read -n 1 -s
    exit 1
fi

# --- Activate the environment ---
echo "Activating conda environment '$CONDA_ENV_NAME'..."

if ! conda activate "$CONDA_ENV_NAME" 2>/dev/null; then
    echo "ERROR: Failed to activate environment '$CONDA_ENV_NAME'."
    echo "Make sure the environment exists. Run _conda_install_env.sh first."
    echo "Press any key to close..."
    read -n 1 -s
    exit 1
fi

echo "Environment '$CONDA_ENV_NAME' activated."
echo ""

# --- Run the application ---
echo "Starting AI Social Network..."
echo "Open http://localhost:8000 in your browser."
echo ""

cd "$SCRIPT_DIR"
python -m src.main
