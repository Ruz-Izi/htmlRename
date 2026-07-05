# ENGLISH COMMENT EXPLAINING THE ENTIRE SCRIPT:
# This bash script outlines the ultimate, modern standard workflow for managing Python environments.
# It addresses the SSL CERTIFICATE_VERIFY_FAILED error which occurs because macOS does not
# link Python's built-in SSL module to the system's root certificates automatically.
# The script uses 'pyenv' (Python Environment) to install and manage Python versions cleanly,
# and 'uv' (Ultra-fast package manager) to create isolated project spaces and install packages.
# By strictly following this workflow, you avoid system Python conflicts and SSL download issues.

# --- 1. Fix SSL Issue for macOS Official Python ---
# Run this ONLY if you are using the official Python installer from python.org
open "/Applications/Python 3.14/Install Certificates.command"

# --- 2. Check and Manage Python Versions with Pyenv ---
# List all installed Python versions
pyenv versions

# Install a specific, stable version of Python (e.g., 3.11.8)
pyenv install 3.11.8

# --- 3. The Standard Project Creation Workflow ---

# Step A: Create a new project directory and enter it
mkdir my_new_project
cd my_new_project

# Step B: Set the local Python version for THIS specific folder
pyenv local 3.11.8

# Step C: Use 'uv' to create a blazing-fast Virtual Environment (VENV)
# 'uv' is much faster and more reliable than standard 'python -m venv'
uv venv

# Step D: Activate the virtual environment (macOS/Linux standard command)
source .venv/bin/activate

# Step E: Check if you are safely inside the virtual environment
which python
which pip

# Step F: Install packages using 'uv pip' (Drop-in replacement for standard pip)
uv pip install flet

# Step G: Check installed packages
uv pip freeze
