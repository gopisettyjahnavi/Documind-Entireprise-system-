"""
Simple web server to serve the frontend files.
Run this alongside the backend API.
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 3001
FRONTEND_DIR = Path(__file__).parent / "frontend"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)
    
    def log_message(self, format, *args):
        print(f"[WEB SERVER] {format % args}")

if __name__ == "__main__":
    os.chdir(FRONTEND_DIR)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🚀 Frontend server running at http://localhost:{PORT}")
        print(f"📁 Serving files from {FRONTEND_DIR}")
        print("Press Ctrl+C to stop")
        httpd.serve_forever()
