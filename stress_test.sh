#!/bin/sh
echo "=== STRESS TEST SCRIPT STARTING ==="
echo "Killing existing firefox..."
pkill -f firefox
sleep 3

log_stats() {
    echo "--- STATS for \$1 TABS ---"
    uptime
    free -m
    echo "--------------------------"
}

echo "Opening 1 tab..."
nohup /home/user/browser_launch.sh 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' > /dev/null 2>&1 &
sleep 20
log_stats 1

echo "Opening 2 more tabs (Total 3)..."
nohup /home/user/browser_launch.sh 'https://www.youtube.com/watch?v=L_jWHffIx5E' 'https://www.youtube.com/watch?v=fJ9rUzIMcZQ' > /dev/null 2>&1 &
sleep 20
log_stats 3

echo "Opening 3 more tabs (Total 6)..."
nohup /home/user/browser_launch.sh 'https://www.youtube.com/watch?v=jNQXAC9IVRw' 'https://www.youtube.com/watch?v=9bZkp7q19f0' 'https://www.youtube.com/watch?v=kJQP7kiw5Fk' > /dev/null 2>&1 &
sleep 25
log_stats 6

echo "Opening 4 more tabs (Total 10)..."
nohup /home/user/browser_launch.sh 'https://www.youtube.com/watch?v=y6120QOlsfU' 'https://www.youtube.com/watch?v=RgKAFK5djSk' 'https://www.youtube.com/watch?v=CevxZvSJLk8' 'https://www.youtube.com/watch?v=JGwWNGJdvx8' > /dev/null 2>&1 &
sleep 30
log_stats 10

echo "=== STRESS TEST COMPLETE ==="
pkill -f firefox
