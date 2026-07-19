#!/bin/sh

echo "============================================================"
echo "Starting Lenovo Tablet Hardware Integration setup..."
echo "WARNING: This script requires root privileges to install"
echo "systemd services and access hardware sensors."
echo "You may be prompted for your sudo password below."
echo "============================================================"

# 0. Setup mDNS (Avahi) for IP changes
echo "Installing mDNS (Avahi) for stable lenovo-hub.local hostname..."
if command -v apk >/dev/null 2>&1; then
    sudo apk add avahi
    sudo rc-update add avahi-daemon default || sudo systemctl enable avahi-daemon
    sudo service avahi-daemon start || sudo systemctl start avahi-daemon
elif command -v apt-get >/dev/null 2>&1; then
    sudo apt-get install -y avahi-daemon
    sudo systemctl enable avahi-daemon
    sudo systemctl start avahi-daemon
fi

# 1. Setup the Webcam Stream
chmod +x setup_webcam.sh
./setup_webcam.sh

# 2. Setup the Hardware API Service
echo "Creating systemd service for Hardware API..."
sudo cp hardware_api.py /usr/local/bin/hardware_api.py
sudo chmod +x /usr/local/bin/hardware_api.py

cat << 'EOF' | sudo tee /etc/systemd/system/hardware-api.service
[Unit]
Description=Lenovo Tablet Hardware API
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 /usr/local/bin/hardware_api.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "Enabling and starting Hardware API service..."
sudo systemctl enable hardware-api.service
sudo systemctl start hardware-api.service


# 3. Setup the Wi-Fi Watchdog
echo "Creating systemd service for Wi-Fi Watchdog..."
sudo cp wifi_watchdog.sh /usr/local/bin/wifi_watchdog.sh
sudo chmod +x /usr/local/bin/wifi_watchdog.sh

cat << 'EOF' | sudo tee /etc/systemd/system/wifi-watchdog.service
[Unit]
Description=Lenovo Tablet Wi-Fi Watchdog
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/wifi_watchdog.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "Enabling and starting Wi-Fi Watchdog..."
sudo systemctl enable wifi-watchdog.service
sudo systemctl start wifi-watchdog.service

echo "============================================================"
echo "Done! The tablet is now broadcasting hardware telemetry on"
echo "port 5000, the webcam on port 8080, and the Wi-Fi Watchdog"
echo "is actively protecting the connection."
echo "The tablet is also now reachable at: lenovo-hub.local"
echo "============================================================"
