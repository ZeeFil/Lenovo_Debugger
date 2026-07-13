import sys
import base64
import subprocess

if len(sys.argv) < 3:
    print("Usage: python3 upload.py <local_file> <remote_path>")
    sys.exit(1)

local_file = sys.argv[1]
remote_path = sys.argv[2]

with open(local_file, "rb") as f:
    content = f.read()

b64_content = base64.b64encode(content).decode('utf-8')
cmd = f"echo '{b64_content}' | base64 -d > {remote_path}"

# Call our existing remote_shell.py
subprocess.run(["python3", "remote_shell.py", cmd])
