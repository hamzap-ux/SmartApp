#!/usr/bin/env bash
# Run SmartApp in dev mode with auto-reload (one command)
export SMARTAPP_DEV=1
export FLASK_ENV=development
echo "Starting SmartApp in development mode (auto-reload enabled)..."
exec python3 main.py
