#!/bin/bash
# Render startup script for ECHOSKETCH
pip install -r requirements.txt
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120