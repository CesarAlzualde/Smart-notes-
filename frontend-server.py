#!/usr/bin/env python3
"""
Simple HTTP server for serving the React frontend files
Compatible with Python 3.6+
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Configuration
PORT = 5174
FRONTEND_DIR = "auth-frontend"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for React SPA routing"""
    
    def do_GET(self):
        # Handle React Router - serve index.html for routes
        if not os.path.exists(self.translate_path(self.path)):
            # If file doesn't exist, serve index.html (for SPA routing)
            if not self.path.startswith('/api'):
                self.path = '/index.html'
        
        # Add CORS headers for development
        return super().do_GET()
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

def main():
    # Change to frontend directory
    frontend_path = Path(__file__).parent / FRONTEND_DIR
    
    if not frontend_path.exists():
        print(f"❌ Error: Frontend directory '{FRONTEND_DIR}' not found")
        sys.exit(1)
    
    # Check for public or src directory
    public_dir = frontend_path / "public"
    src_dir = frontend_path / "src"
    
    if public_dir.exists():
        os.chdir(public_dir)
        print(f"📁 Serving from: {public_dir}")
    elif src_dir.exists():
        os.chdir(frontend_path)
        print(f"📁 Serving from: {frontend_path}")
    else:
        os.chdir(frontend_path) 
        print(f"📁 Serving from: {frontend_path}")
    
    # Create server
    handler = CustomHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            print("🚀 Frontend Server Started!")
            print(f"📡 URL: http://localhost:{PORT}")
            print(f"🔧 Backend: http://localhost:5000")
            print("❌ Press Ctrl+C to stop")
            print("-" * 50)
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n✅ Server stopped by user")
    except OSError as e:
        if e.errno == 10048:  # Port already in use
            print(f"❌ Error: Port {PORT} is already in use")
            print("💡 Try closing other applications or use a different port")
        else:
            print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
