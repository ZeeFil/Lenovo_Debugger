import sys
import json
import time
import urllib.request
import urllib.error

PROJECT_ID = "gen-lang-client-0915242393"
DATABASE_ID = "(default)"
DOC_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/{DATABASE_ID}/documents/device_sync/target"

def send_command(command):
    data = {
        "fields": {
            "command": {"stringValue": command},
            "status": {"stringValue": "PENDING"},
            "output": {"stringValue": ""},
            "timestamp": {"integerValue": str(int(time.time() * 1000))}
        }
    }
    
    req = urllib.request.Request(DOC_URL, data=json.dumps(data).encode(), method='PATCH')
    req.add_header('Content-Type', 'application/json')
    
    try:
        urllib.request.urlopen(req)
        print(f"[*] Sent command: {command}")
    except urllib.error.URLError as e:
        print(f"[!] Error sending command: {e}")
        sys.exit(1)

def wait_for_result():
    print("[*] Waiting for response...", end='', flush=True)
    while True:
        try:
            req = urllib.request.Request(DOC_URL)
            with urllib.request.urlopen(req) as response:
                doc = json.loads(response.read().decode())
                fields = doc.get('fields', {})
                status = fields.get('status', {}).get('stringValue', '')
                if status == 'COMPLETED':
                    output = fields.get('output', {}).get('stringValue', '')
                    print("\n" + "="*40)
                    print(output)
                    print("="*40)
                    return
        except Exception:
            pass
        
        print(".", end='', flush=True)
        time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 remote_shell.py <command>")
        sys.exit(1)
        
    cmd = " ".join(sys.argv[1:])
    send_command(cmd)
    wait_for_result()
