#!/bin/bash

pip3 install -r requirements.txt

bash sync.sh

crond -L cron.log

bash /entrypoint.sh
