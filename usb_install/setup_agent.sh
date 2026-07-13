#!/bin/sh
# Lenovo Tablet USB Installer for Cloud Relay Agent

set -e

echo "Starting Lenovo Tablet Cloud Relay Agent installation..."

# 1. Ensure Python 3 is installed
if ! command -v python3 > /dev/null 2>&1; then
    echo "Error: python3 is not installed. Please install Python 3 first."
    exit 1
fi

# 2. Get the directory this script is running from
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 3. Copy or download the agent script to the user's home directory
echo "Installing tablet_agent.py to home directory..."
if [ -f "$SCRIPT_DIR/tablet_agent.py" ]; then
    cp "$SCRIPT_DIR/tablet_agent.py" "$HOME/tablet_agent.py"
else
    echo "Downloading tablet_agent.py from server..."
    wget -q -O "$HOME/tablet_agent.py" https://gen-lang-client-0915242393.web.app/tablet_agent.py || curl -s -o "$HOME/tablet_agent.py" https://gen-lang-client-0915242393.web.app/tablet_agent.py
fi
chmod +x "$HOME/tablet_agent.py"

# 4. Update the Sway config to start the agent automatically
SWAY_CONFIG="$HOME/.config/sway/config"
AGENT_CMD="exec python3 $HOME/tablet_agent.py"

if [ -f "$SWAY_CONFIG" ]; then
    if grep -qF "$AGENT_CMD" "$SWAY_CONFIG"; then
        echo "Agent is already configured to start in Sway!"
    else
        echo "Adding agent to Sway autostart configuration..."
        echo "" >> "$SWAY_CONFIG"
        echo "# Autostart Cloud Relay Agent" >> "$SWAY_CONFIG"
        echo "$AGENT_CMD" >> "$SWAY_CONFIG"
        echo "Sway config updated successfully."
    fi
else
    echo "Warning: Sway config not found at $SWAY_CONFIG."
    echo "You will need to manually add '$AGENT_CMD' to your window manager's autostart."
fi

echo "======================================"
echo "Installation complete!"
echo "To test it right now, you can manually run:"
echo "python3 ~/tablet_agent.py"
echo "Or just reboot your tablet to have it start automatically."
echo "======================================"
