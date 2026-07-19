import sys
import json
import tinytuya

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 lenovo_plug.py [on|off|status]")
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    
    try:
        with open("/home/zfil/Lenovo_Smarthome_Hub/plug_config.json", "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error reading config: {e}")
        sys.exit(1)
        
    if config["device_id"] == "REPLACE_WITH_DEVICE_ID":
        print(f"MOCK SUCCESS: Lenovo Smart Plug (Light) turned {cmd.upper()} (Waiting for user to configure real keys in plug_config.json)")
        sys.exit(0)
        
    try:
        d = tinytuya.OutletDevice(
            dev_id=config["device_id"],
            address=config["ip_address"],
            local_key=config["local_key"],
            version=config.get("version", 3.3)
        )
        
        if cmd == "on":
            d.turn_on()
            print("Turned ON")
        elif cmd == "off":
            d.turn_off()
            print("Turned OFF")
        elif cmd == "status":
            print(d.status())
        else:
            print("Unknown command")
            
    except Exception as e:
        print(f"Error controlling device: {e}")

if __name__ == "__main__":
    main()
