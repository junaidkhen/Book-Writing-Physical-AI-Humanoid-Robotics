#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Set a clean PATH with properly quoted paths
export PATH="/home/junaidkh84/.local/bin:/home/junaidkh84/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/wsl/lib:/snap/bin"

# Start the uvicorn server
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload