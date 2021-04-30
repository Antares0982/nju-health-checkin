#!/bin/bash

set -e

RESULT=$(python checkin.py)

echo "$RESULT"

# for telegram message
echo "::set-output name=message::${RESULT}"
