# api/hello.py
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):              # ← 必須叫 handler
    def do_GET(self):
        body = json.dumps({"message": "Hello from Vercel Python!"}).encode()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
