#!/bin/bash

shell_dir=$(dirname $(readlink -f "$0"))

RESULT=$(TO_HTML=1 python3 $shell_dir/checkin.py 2>&1)

echo "$RESULT"

if [[ -z $bottoken || -z $tgid ]]; then
    echo "no tgid or bot token"
    exit
fi

# for telegram message

curl "https://api.telegram.org/bot${bottoken}/sendMessage?chat_id=${tgid}&text=${RESULT}"
