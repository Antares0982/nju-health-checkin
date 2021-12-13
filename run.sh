#!/bin/bash

set -e

RESULT=$(python3 checkin.py)

echo "$RESULT"

# for telegram message

curl -s "https://api.telegram.org/bot${token}/sendMessage?chat_id=${tgid}&text=${RESULT}"
