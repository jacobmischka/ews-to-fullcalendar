#!/bin/bash

echo "[$(date)] Starting sync..."

python3 ews_to_fullcalendar.py --sync --quiet && echo "[$(date)] Synced!"
