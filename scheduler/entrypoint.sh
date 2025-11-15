#!/bin/bash

echo "[scheduler] Starting cron for daily collector..."
cron

# keep container alive
touch /var/log/cron.log
tail -f /var/log/cron.log