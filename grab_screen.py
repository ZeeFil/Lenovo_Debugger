import subprocess
import base64

# run remote shell
proc = subprocess.run(["python3", "remote_shell.py", "WAYLAND_DISPLAY=wayland-1 XDG_RUNTIME_DIR=/run/user/10000 grim - | base64"], capture_output=True, text=True)
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

with open("/home/zfil/.gemini/antigravity/brain/1cde323c-b8ba-45bb-a92f-0bb3ebb6b483/tablet_screen.png", "wb") as f:
    f.write(base64.b64decode(b64_data))
print("Done")
