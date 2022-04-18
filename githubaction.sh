#!/bin/bash

set -e

RESULT=$(python checkin.py)

echo "$RESULT"

towho=$TELEGRAM_TO
bottoken=$TELEGRAM_TOKEN

# for telegram message
curl "https://api.telegram.org/bot${bottoken}/sendMessage?chat_id=${towho}&text=${RESULT}"
