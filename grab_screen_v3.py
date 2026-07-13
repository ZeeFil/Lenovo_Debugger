import subprocess
import base64
import time
import sys

# run swaynag
cmd = "pkill swaynag; XDG_RUNTIME_DIR=/run/user/10000 WAYLAND_DISPLAY=wayland-1 swaynag -t power -e bottom -f 'Google Sans 20' --background 1E1E2EFF --text CAD3F5FF --button-background 45475AFF --button-text CAD3F5FF --border 1E1E2EFF --border-bottom ED8796FF --border-bottom-size 4 --button-border-size 0 --button-padding 14 --button-gap 20 --button-dismiss-gap 20 --button-margin-right 20 --message-padding 20 -m '  Power off the tablet?' -Z '  Yes, Power Off' 'echo noop' -s '  Cancel' > /dev/null 2>&1 & sleep 2 && XDG_RUNTIME_DIR=/run/user/10000 WAYLAND_DISPLAY=wayland-1 grim -g '0 1000 1280 280' - | base64"

print("Grabbing screen...")
proc = subprocess.run(["python3", "remote_shell.py", cmd], capture_output=True, text=True)
out = proc.stdout

# parse between ============
lines = out.splitlines()
in_content = False
b64_data = ""
for line in lines:
    if "========" in line:
        in_content = not in_content
        continue
    if in_content:
        b64_data += line.strip()

if not b64_data:
    print("Failed to get screenshot data")
    sys.exit(1)

with open("/home/zfil/.gemini/antigravity/brain/b47d5d17-9a01-4d4b-b230-e9312acebc51/swaynag_power_v3.png", "wb") as f:
    f.write(base64.b64decode(b64_data))
print("Done")
