#!/bin/bash

while true; do
    current_time=$(date +%H:%M)
    if [[ "$current_time" == "02:30" ]]; then
        pkill -f "main.py"
        sudo python3 app.py &
    fi
    sleep 60
done