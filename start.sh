#!/bin/sh
CRON_INTERVAL=$(printenv CRON_INTERVAL)
sed -i "s/\$CRON_INTERVAL/$CRON_INTERVAL/" /etc/crontabs/root
exec crond -f -d 8