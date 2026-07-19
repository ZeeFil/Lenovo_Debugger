import subprocess
import base64
import sys

cmd = "XDG_RUNTIME_DIR=/run/user/10000 WAYLAND_DISPLAY=wayland-1 grim - | base64"
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

with open("/home/zfil/.gemini/antigravity/brain/35d32745-2a29-4ac9-ab30-44529703a4a8/latest_screen.png", "wb") as f:
    f.write(base64.b64decode(b64_data))
print("Done")
