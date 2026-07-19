import time
import subprocess
import socketserver
from http.server import BaseHTTPRequestHandler, HTTPServer

class CameraHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/?action=stream':
            self.send_response(200)
            self.send_header('Age', '0')
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    # capture screen using grim, as jpeg, scale to 0.5 for performance
                    env = {'XDG_RUNTIME_DIR': '/run/user/10000', 'WAYLAND_DISPLAY': 'wayland-1'}
                    result = subprocess.run(
                        ['grim', '-t', 'jpeg', '-s', '0.5', '-q', '50', '-'], 
                        capture_output=True, 
                        env=env
                    )
                    
                    if result.returncode == 0:
                        jpg = result.stdout
                        self.wfile.write(b'--FRAME\r\n')
                        self.send_header('Content-Type', 'image/jpeg')
                        self.send_header('Content-Length', str(len(jpg)))
                        self.end_headers()
                        self.wfile.write(jpg)
                        self.wfile.write(b'\r\n')
                    
                    # 5 fps
                    time.sleep(0.2)
            except Exception as e:
                pass
        else:
            self.send_error(404)

class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

if __name__ == '__main__':
    server = ThreadingHTTPServer(('0.0.0.0', 8080), CameraHandler)
    print("Serving MJPEG screen stream on port 8080...")
    server.serve_forever()
