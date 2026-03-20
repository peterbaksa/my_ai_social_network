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

# --- Read Python version ---
PYTHON_VERSION_FILE="$SCRIPT_DIR/_python_version"

if [ ! -f "$PYTHON_VERSION_FILE" ]; then
    echo "ERROR: File '$PYTHON_VERSION_FILE' not found."
    echo "Press any key to close..."
    read -n 1 -s
    exit 1
fi

PYTHON_VERSION="$(cat "$PYTHON_VERSION_FILE" | tr -d '[:space:]')"

if [ -z "$PYTHON_VERSION" ]; then
    echo "ERROR: File '$PYTHON_VERSION_FILE' is empty or does not contain a valid Python version."
    echo "Press any key to close..."
    read -n 1 -s
    exit 1
fi

echo "Conda environment: $CONDA_ENV_NAME"
echo "Python version:    $PYTHON_VERSION"
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

# --- Check if environment already exists ---
if conda env list | grep -qw "$CONDA_ENV_NAME"; then
    echo "Environment '$CONDA_ENV_NAME' already exists. No installation needed."
    echo ""
    echo "Press any key to close..."
    read -n 1 -s
    exit 0
fi

# --- Create the environment ---
echo "Creating conda environment '$CONDA_ENV_NAME' with Python $PYTHON_VERSION ..."
echo ""

if conda create -n "$CONDA_ENV_NAME" python="$PYTHON_VERSION" -y; then
    echo ""
    echo "Environment '$CONDA_ENV_NAME' was successfully created."
else
    echo ""
    echo "ERROR: Failed to create environment '$CONDA_ENV_NAME'."
    echo "Press any key to close..."
    read -n 1 -s
    exit 1
fi

echo ""
echo "Press any key to close..."
read -n 1 -s
exit 0
