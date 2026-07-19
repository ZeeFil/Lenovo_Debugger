#!/usr/bin/env python3
import json
import os
import glob
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

def read_sysfs(path):
    try:
        with open(path, 'r') as f:
            return f.read().strip()
    except Exception:
        return None

def get_battery_info():
    bat_paths = glob.glob('/sys/class/power_supply/BAT*')
    if not bat_paths:
        bat_paths = glob.glob('/sys/class/power_supply/*bat*')
        
    if bat_paths:
        path = bat_paths[0]
        capacity = read_sysfs(os.path.join(path, 'capacity'))
        status = read_sysfs(os.path.join(path, 'status'))
        return {
            "capacity": int(capacity) if capacity and capacity.isdigit() else None,
            "status": status if status else None
        }
    return {"capacity": None, "status": None}

def get_ambient_light():
    light_paths = glob.glob('/sys/bus/iio/devices/iio:device*/in_illuminance_raw')
    if light_paths:
        val = read_sysfs(light_paths[0])
        return int(val) if val and val.isdigit() else None
    return None

def check_tamper():
    accel_x = glob.glob('/sys/bus/iio/devices/iio:device*/in_accel_x_raw')
    if accel_x:
        val = read_sysfs(accel_x[0])
        if val is None:
             return {"status": "Unknown"}
        return {"status": "Secure", "raw_x": val}
    return {"status": "Unknown"}

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 20. Security Rule Fallback (Lock CORS to Local Network)
        client_ip = self.client_address[0]
        if not (client_ip.startswith('192.168.') or 
                client_ip.startswith('10.') or 
                client_ip.startswith('172.') or 
                client_ip == '127.0.0.1'):
            self.send_response(403)
            self.end_headers()
            return

        if self.path == '/api/hardware':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            # Allow origin specifically for local dashboard
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            data = {
                "timestamp": time.time(),
                "battery": get_battery_info(),
                "light_level": get_ambient_light(),
                "security": check_tamper()
            }
            
            try:
                self.wfile.write(json.dumps(data).encode('utf-8'))
            except BrokenPipeError:
                pass # Client disconnected before receiving data
        else:
            self.send_response(404)
            self.end_headers()

def run(server_class=HTTPServer, handler_class=RequestHandler, port=5000):
    server_address = ('0.0.0.0', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting hardware API on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
