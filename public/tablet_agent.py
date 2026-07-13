import urllib.request
import urllib.error
import json
import time
import subprocess

PROJECT_ID = "gen-lang-client-0915242393"
DOC_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/device_sync/target"

def get_document():
    try:
        req = urllib.request.Request(DOC_URL)
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        print(f"HTTP Error: {e.code}")
    except Exception as e:
        print(f"Error fetching document: {e}")
    return None

def update_document(status, output):
    data = {
        "fields": {
            "status": {"stringValue": status},
            "output": {"stringValue": output},
            "timestamp": {"integerValue": str(int(time.time() * 1000))}
        }
    }
    # Notice we use updateMask so we don't accidentally overwrite the command field entirely
    url = f"{DOC_URL}?updateMask.fieldPaths=status&updateMask.fieldPaths=output&updateMask.fieldPaths=timestamp"
    req = urllib.request.Request(url, data=json.dumps(data).encode(), method='PATCH')
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req) as response:
            pass
    except Exception as e:
        print(f"Error updating document: {e}")

print("Listening for commands from Cloud Relay...")
while True:
    doc = get_document()
    if doc and 'fields' in doc:
        fields = doc['fields']
        status = fields.get('status', {}).get('stringValue', '')
        
        if status == "PENDING":
            command = fields.get('command', {}).get('stringValue', '')
            print(f"Executing: {command}")
            
            # Execute command
            try:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    timeout=30 # Prevent hanging forever
                )
                output = result.stdout
                if result.stderr:
                    output += "\n[STDERR]\n" + result.stderr
            except Exception as e:
                output = str(e)
                
            print(f"Command finished. Updating status to COMPLETED.")
            update_document("COMPLETED", output)
            
    time.sleep(2)
