#!/bin/bash

# minimum age of directories to remove, in minutes:
AGE=60

# crontab example:
# 0 * * * * /path/to/Dispatch/remove_outputs.sh

cd "$(dirname "$0")"
find ./app/modules/common/AD/F16_input/static/ -type d -name "20??-??-??-??-??-??-*" -cmin +$AGE -exec rm -rf \{\} \;

