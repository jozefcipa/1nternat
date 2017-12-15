#!/bin/bash

# Write out current crontab
crontab -l > _crontab

# Echo new cron into cron file
echo "*/5 * * * * python3 /home/joci/1nternat/app.py " >> _crontab  # Runs every 5 minutes
echo "0 3 * * * python3 /home/joci/1nternat/app.py --turn-ports-off " >> _crontab  # Runs every day at 3am to turn off ports
echo "00 00 * * * python3 /home/joci/1nternat/autoupdate.py " >> _crontab  # Checks for update every day at midnight

# Install new cron file
crontab _crontab
rm _crontab
