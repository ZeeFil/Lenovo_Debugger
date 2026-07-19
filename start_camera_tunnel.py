import subprocess
import time
import re
import sys
import os

# Kill existing servers and tunnels
subprocess.run(['pkill', '-f', 'mjpeg_screen_server.py'])
subprocess.run(['pkill', '-f', 'cloudflared'])
time.sleep(0.5)

# Start MJPEG server in background
subprocess.Popen(['python3', 'mjpeg_screen_server.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Start Cloudflare tunnel
proc = subprocess.Popen(['./cloudflared', 'tunnel', '--url', 'http://localhost:8080'], stderr=subprocess.PIPE, text=True)

url = None
start_time = time.time()

# Read stderr until we find the URL or timeout
while time.time() - start_time < 10:
    line = proc.stderr.readline()
    if not line:
        continue
    match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
    if match:
        url = match.group(0)
        break

# We must close stderr so we don't block
proc.stderr.close()

if url:
    # Print the URL so executeCloudCommand can capture it
    print(url)
    sys.exit(0)
else:
    print("FAILED_TO_START_TUNNEL")
    sys.exit(1)
