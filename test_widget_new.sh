#!/bin/sh
echo "Starting 20 tests..."
export SWAYSOCK=$(find /run/user/10000 -name "sway-ipc*.sock" | head -n 1)
for i in $(seq 1 20); do
    pkill -f widget.py
    swaymsg exec "python3 /home/user/widget.py > /home/user/widget_error.log 2>&1"
    sleep 1
    echo "Test $i complete"
done
echo "All tests finished!"
