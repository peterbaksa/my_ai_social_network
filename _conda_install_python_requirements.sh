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

# --- Find requirements.txt ---
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "ERROR: File '$REQUIREMENTS_FILE' not found."
    echo "Press any key to close..."
    read -n 1 -s
    exit 1
fi

if [ ! -s "$REQUIREMENTS_FILE" ]; then
    echo "ERROR: File '$REQUIREMENTS_FILE' is empty."
    echo "Press any key to close..."
    read -n 1 -s
    exit 1
fi

echo "Conda environment: $CONDA_ENV_NAME"
echo "Requirements file: $REQUIREMENTS_FILE"
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

# --- Install requirements ---
echo "Installing Python requirements from '$REQUIREMENTS_FILE'..."
echo ""

if pip install -r "$REQUIREMENTS_FILE"; then
    echo ""
    echo "All requirements installed successfully."
else
    echo ""
    echo "ERROR: Failed to install some requirements."
    echo "Press any key to close..."
    read -n 1 -s
    exit 1
fi

echo ""
echo "Press any key to close..."
read -n 1 -s
exit 0
