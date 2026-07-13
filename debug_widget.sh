#!/bin/sh
export XDG_RUNTIME_DIR=/run/user/10000
export WAYLAND_DISPLAY=wayland-1
export WAYLAND_DEBUG=1
python3 /home/user/widget.py > /home/user/wl_debug.log 2>&1 &
echo $! > /home/user/widget.pid
sleep 2
cat /home/user/wl_debug.log | grep -E '(wl_surface|zwlr_layer_surface)' | tail -n 20 > /home/user/wl_debug_summary.log
