#!/bin/bash

pip3 install -r requirements.txt

bash sync.sh

crond

bash /entrypoint.sh
