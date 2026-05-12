#!/usr/bin/env python3
"""
知乎 OAuth 回调服务器 - 知遇圈 Demo（纯标准库版本，无需安装依赖）
功能：接收知乎授权回调，显示授权码，然后跳转回 Demo 页面
"""
import http.server
import urllib.parse
import urllib.request
import json
import time
import threading
import webbrowser
import sys
import socket

# ==================== 配置区 ====================
APP_ID = "261"
APP_KEY = "f3b623315d894088980c86d17a592e72"
CALLBACK_BASE = "http://127.0.0.1:5189"   # 本地回调地址
DEMO_BASE = "http://127.0.0.1:5188"        # Demo 页面地址

# ==================== 工具函数 ====================
def get_local_ip():
    """获取本机局域网 IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.x.x"

def auto_update_callback():
    """自动更新回调地址为局域网IP，方便手机访问"""
    global CALLBACK_BASE, DEMO_BASE
    local_ip = get_local_ip()
    CALLBACK_BASE = f"http://{local_ip}:5189"
    DEMO_BASE = f"http://{local_ip}:5188"

# ==================== HTTP 服务器 ====================
class OAuthHandler(http.server.BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        """美化日志输出"""
        print(f"[{time.strftime('%H:%M:%S')}] {args[0]}")
    
    def send_html(self, content, code=200):
        """发送 HTML 响应"""
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("X-Frame-Options", "DENY")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))
    
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)
        
        if path == "/" or path == "/index":
            self.handle_index()
        elif path == "/callback":
            self.handle_callback(params)
        else:
            self.send_html("<h1>404 Not Found</h1><p>请访问 <a href='/'>首页</a></p>", 404)
    
    def handle_index(self):
        """调试页面"""
        oauth_url = (
            f"https://www.zhihu.com/oauth/authorize"
            f"?client_id={APP_ID}"
            f"&response_type=code"
            f"&redirect_uri={urllib.parse.quote(CALLBACK_BASE + '/callback')}"
            f"&scope=zhihu_id,zhihu_profile"
            f"&state=xyz_hackathon_2026"
        )
        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>知遇圈 OAuth 调试工具</title>
<style>
body{{font-family:'Helvetica Neue',sans-serif;background:#0D1B3E;color:white;margin:0;padding:30px;min-height:100vh;box-sizing:border-box}}
h1{{color:#F7B955;margin:0 0 8px}}
.sub{{color:#86909C;margin:0 0 30px;font-size:14px}}
.box{{background:#1A1A2E;border-radius:12px;padding:20px;margin:16px 0;font-size:14px}}
.label{{color:#86909C;font-size:12px;margin-bottom:4px}}
.value{{color:#00C48C;font-family:'Courier New',monospace;word-break:break-all}}
.url-box{{background:#0D1B3E;border:1px solid #2a3a6e;border-radius:8px;padding:14px;word-break:break-all;font-size:13px;line-height:1.8}}
.btn{{display:inline-block;background:#0066FF;color:white;padding:12px 28px;border-radius:10px;text-decoration:none;font-size:16px;margin:10px 10px 10px 0;cursor:pointer;border:none}}
.btn:hover{{background:#0052CC}}
.btn-green{{background:#00C48C}}
ol{{line-height:2.2;padding-left:24px;font-size:14px;color:#ccc}}
.warning{{background:#2a1a0a;border:1px solid #F7B955;border-radius:12px;padding:20px;margin-top:30px}}
.warning h3{{color:#F7B955;margin:0 0 12px}}
.tip{{background:#0a2a1a;border-radius:8px;padding:14px;margin:12px 0;font-size:13px;color:#00C48C}}
</style>
</head>
<body>
<h1>知遇圈 OAuth 调试工具</h1>
<p class="sub">知乎引力场 × 社交 黑客松 Demo</p>

<div class="box">
<div class="label">APP_ID</div>
<div class="value">{APP_ID}</div>
</div>

<div class="box">
<div class="label">回调地址（Callback URL）</div>
<div class="value">{CALLBACK_BASE}/callback</div>
</div>

<div class="box">
<div class="label">Demo 页面地址</div>
<div class="value">{DEMO_BASE}/index.html</div>
</div>

<div class="box">
<div class="label">完整 OAuth 授权 URL</div>
<div class="url-box">{oauth_url}</div>
</div>

<p><a class="btn" href="{oauth_url}" target="_blank">在浏览器打开知乎授权页</a>
<a class="btn btn-green" href="/callback?code=DEMO_CODE_123456&state=xyz_hackathon_2026">模拟回调（开发测试用）</a></p>

<div class="warning">
<h3>手机端使用说明</h3>
<ol>
<li>确认手机和电脑连的是<b>同一个 WiFi</b></li>
<li>把回调地址改为：<code>{CALLBACK_BASE}/callback</code></li>
<li>在知乎开放平台后台重新填写回调地址</li>
<li>手机浏览器打开 Demo，点击"授权知乎账号登录"</li>
<li>授权完成后浏览器显示授权码，3秒后自动跳转回 Demo</li>
</ol>
</div>

<div class="tip">
提示：回调地址需要在知乎开放平台后台「设置 → 安全设置 → 授权回调页」中配置为：<br>
<strong>{CALLBACK_BASE}/callback</strong>
</div>
</body>
</html>"""
        self.send_html(html)
    
    def handle_callback(self, params):
        """处理知乎 OAuth 回调"""
        code = params.get('code', [''])[0]
        state = params.get('state', [''])[0]
        
        if not code:
            self.send_html("""<html><body style="font-family:sans-serif;padding:40px;text-align:center;">
            <h2 style="color:#e74c3c;">授权失败</h2><p>未收到授权码，<a href="/">重试</a></p></body></html>""")
            return
        
        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>授权成功 - 知遇圈</title>
<style>
body{{font-family:'Helvetica Neue',sans-serif;background:linear-gradient(135deg,#0D1B3E,#0066FF);min-height:100vh;margin:0;display:flex;align-items:center;justify-content:center;padding:20px;box-sizing:border-box}}
.card{{background:white;border-radius:20px;padding:40px;max-width:500px;width:100%;text-align:center;box-shadow:0 24px 80px rgba(0,0,0,0.35)}}
.badge{{background:#00C48C;color:white;padding:6px 20px;border-radius:20px;font-size:14px;display:inline-block;margin-bottom:20px;font-weight:500}}
h1{{color:#1A1A2E;margin:0 0 8px;font-size:22px}}
p{{color:#86909C;margin:0 0 24px;font-size:14px}}
.code-box{{background:#F8F9FB;border:1px solid #E8EBF0;border-radius:12px;padding:16px;margin:16px 0;text-align:left}}
.label{{font-size:12px;color:#86909C;margin-bottom:8px}}
.code{{font-family:'Courier New',monospace;font-size:13px;color:#0066FF;word-break:break-all;background:#EEF4FF;padding:8px;border-radius:6px;display:block}}
.btn{{display:inline-block;background:#0066FF;color:white;padding:14px 36px;border-radius:12px;text-decoration:none;font-size:16px;font-weight:500;margin-top:10px}}
.btn:hover{{background:#0052CC}}
.countdown{{color:#86909C;font-size:13px;margin-top:16px}}
@keyframes fade{{from{{opacity:1}}to{{opacity:0.3}}}}
.fade{{animation:fade 1s infinite alternate}}
</style>
</head>
<body>
<div class="card">
<div class="badge">授权成功</div>
<h1>知乎账号授权完成</h1>
<p>正在准备进入知遇圈...</p>

<div class="code-box">
<div class="label">授权码 (Authorization Code)</div>
<span class="code">{code}</span>
</div>

<p style="font-size:13px;color:#86909C;">
授权码已收到，正在换取用户身份令牌。<br>
接下来将自动进入 AI 用户画像生成流程。
</p>

<a class="btn" href="{DEMO_BASE}/index.html?auth_code={urllib.parse.quote(code)}&state={urllib.parse.quote(state)}">
继续进入知遇圈
</a>

<p class="countdown fade" id="cd">页面将在 <span id="sec">5</span> 秒后自动跳转...</p>
</div>

<script>
let s = 5;
function tick(){{
    document.getElementById('sec').textContent = s;
    if(s <= 0){{
        window.location.href = '{DEMO_BASE}/index.html?auth_code={urllib.parse.quote(code)}&state={urllib.parse.quote(state)}';
    }} else {{
        s--;
        setTimeout(tick, 1000);
    }}
}}
setTimeout(tick, 500);
</script>
</body>
</html>"""
        self.send_html(html)

# ==================== 启动服务器 ====================
if __name__ == "__main__":
    auto_update_callback()
    local_ip = get_local_ip()
    
    print(f"\n{'='*50}")
    print(f"  知遇圈 OAuth 回调服务器")
    print(f"{'='*50}")
    print(f"  Demo 页面:   {DEMO_BASE}/index.html")
    print(f"  回调地址:    {CALLBACK_BASE}/callback")
    print(f"  手机 Demo:   http://{local_ip}:5188/index.html")
    print(f"{'='*50}")
    print(f"  调试页面: http://127.0.0.1:5189/")
    print(f"  ⚠️  请在知乎开放平台后台设置回调地址为：")
    print(f"     {CALLBACK_BASE}/callback")
    print(f"{'='*50}\n")
    
    server = http.server.HTTPServer(("0.0.0.0", 5189), OAuthHandler)
    server.serve_forever()
