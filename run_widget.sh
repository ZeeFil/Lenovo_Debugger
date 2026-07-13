#!/bin/sh
export XDG_RUNTIME_DIR=/run/user/10000
export WAYLAND_DISPLAY=wayland-1
python3 /home/user/widget.py > /home/user/widget_error.log 2>&1
echo "Widget script exited with code $?" >> /home/user/widget_error.log
