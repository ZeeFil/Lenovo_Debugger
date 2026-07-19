#!/bin/sh
echo "Starting 25 tests..."
for i in $(seq 1 25); do
    pkill -f widget.py
    sh /home/user/run_widget.sh &
    sleep 1
    echo "Test $i complete"
done
echo "All tests finished!"
