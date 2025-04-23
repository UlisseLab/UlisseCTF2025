#!/bin/sh
env PYTHONPYCACHEPREFIX=/tmp uv run gunicorn --workers 2 --worker-class gevent --log-level debug --worker-connections 128 --bind "0.0.0.0:8000" --reload 'app:app' 