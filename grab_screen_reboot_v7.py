import subprocess
import base64
import time
import sys

# run polished swaynag for reboot with centered styling
cmd = "pkill swaynag; XDG_RUNTIME_DIR=/run/user/10000 WAYLAND_DISPLAY=wayland-1 swaynag -t reboot -e bottom -f 'Inter 14' --background 1E1E2EFF --text CAD3F5FF --button-background 45475AFF --button-text CAD3F5FF --border 1E1E2EFF --border-bottom-size 0 --button-border-size 0 --button-padding 8 --button-gap 8 --button-dismiss-gap 8 --button-margin-right 0 --message-padding 8 -m ' Reboot the tablet?' -Z ' Yes, Reboot' 'echo noop' -s ' Cancel' > /dev/null 2>&1 & sleep 2 && XDG_RUNTIME_DIR=/run/user/10000 WAYLAND_DISPLAY=wayland-1 grim -g '0,600 1280x200' - | base64"

print("Grabbing screen...")
proc = subprocess.run(["python3", "remote_shell.py", cmd], capture_output=True, text=True)
out = proc.stdout

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

with open("/home/zfil/.gemini/antigravity/brain/b47d5d17-9a01-4d4b-b230-e9312acebc51/swaynag_reboot_preview_v7.png", "wb") as f:
    f.write(base64.b64decode(b64_data))
print("Done")
