#!/bin/sh

echo "Installing webcam streaming packages..."
# PostmarketOS is based on Alpine Linux, so we use apk
sudo apk add mjpg-streamer v4l-utils

echo "Creating systemd service for mjpg-streamer..."
cat << 'EOF' | sudo tee /etc/systemd/system/webcam-stream.service
[Unit]
Description=Webcam MJPEG Streamer
After=network.target

[Service]
User=root
ExecStart=/usr/bin/mjpg_streamer -i "input_uvc.so -d /dev/video0 -r 1280x720 -f 30" -o "output_http.so -p 8080 -w /usr/share/mjpg-streamer/www"
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "Enabling and starting webcam stream..."
sudo systemctl enable webcam-stream.service
sudo systemctl start webcam-stream.service
echo "Webcam stream is active on port 8080!"
