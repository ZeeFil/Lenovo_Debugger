import subprocess
import base64
import sys

cmd = "pkill swaynag; XDG_RUNTIME_DIR=/run/user/10000 WAYLAND_DISPLAY=wayland-1 swaynag -t power -e top -f 'Google Sans 20' --background 1E1E2EFF --text CAD3F5FF --button-background 45475AFF --button-text CAD3F5FF --border 1E1E2EFF --border-bottom ED8796FF --border-bottom-size 4 --button-border-size 0 --button-padding 14 --button-gap 20 --button-dismiss-gap 20 --button-margin-right 20 --message-padding 20 -m '  Power off the tablet?' -Z '  Yes, Power Off' 'echo noop' -s '  Cancel' > /dev/null 2>&1 & sleep 2 && XDG_RUNTIME_DIR=/run/user/10000 WAYLAND_DISPLAY=wayland-1 grim /tmp/scr_part.png"

subprocess.run(cmd, shell=True)

with open("/tmp/scr_part.png", "rb") as f:
    b64_data = base64.b64encode(f.read()).decode("utf-8")

print("---START_B64---")
print(b64_data)
print("---END_B64---")
