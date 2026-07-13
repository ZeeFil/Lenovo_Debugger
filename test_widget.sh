#!/bin/sh
echo "Starting 20 tests..."
for i in $(seq 1 20); do
    pkill -f widget.py
    SWAYSOCK=/run/user/10000/sway-ipc.10000.17824.sock swaymsg exec python3 /home/user/widget.py
    sleep 1
    echo "Test $i complete"
done
echo "All tests finished!"
