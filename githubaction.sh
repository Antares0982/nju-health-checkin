#!/bin/bash

set -e

RESULT=$(TO_HTML=1 python checkin.py)

echo "$RESULT"

towho=$TELEGRAM_TO
bottoken=$TELEGRAM_TOKEN

if [[ -z $bottoken || -z $towho ]]; then
    echo "no tgid or bot token"
    exit
fi

# for telegram message
curl "https://api.telegram.org/bot${bottoken}/sendMessage?chat_id=${towho}&text=${RESULT}"
