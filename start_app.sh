#!/bin/bash
python3 -m venv /app/action-recorder/venv && \
source /app/action-recorder/venv/bin/activate && \
pip install -r /app/action-recorder/requirements.txt && \
python /app/action-recorder/main.py > /app/action-recorder/logs.txt