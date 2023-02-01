#!/bin/bash

while true; do
    current_time=$(date +%H:%M)
    if [[ "$current_time" == "04:00" ]]; then
        pkill -f "main.py"
        sudo python3 main.py &
    fi
    sleep 60
done