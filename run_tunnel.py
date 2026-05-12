#!/usr/bin/env python3
"""启动 localtunnel 并捕获公网链接"""
import subprocess
import re
import time
import os

print("正在启动 localtunnel 公网穿透...")

proc = subprocess.Popen(
    [r"C:\Program Files\nodejs\npx.cmd", "--yes", "localtunnel", "--port", "5188"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    cwd=r"c:\Users\wukangning\WorkBuddy\20260512135511\zhiyuquan-demo"
)

url_file = os.path.join(os.path.dirname(__file__), "public_url.txt")
found = False

for line in proc.stdout:
    print(line.rstrip())
    # localtunnel 输出类似: "your url is: https://your-url.loca.lt"
    match = re.search(r"(https://\S+\.loca\.lt)", line)
    if match:
        url = match.group(1)
        with open(url_file, "w") as f:
            f.write(url)
        print(f"\n✅ 公网链接已保存到: {url_file}")
        print(f"🔗 {url}")
        found = True
        break

if not found:
    print("等待 localtunnel 启动（最多30秒）...")
    for i in range(30):
        time.sleep(1)
        # 再检查一次文件
        if os.path.exists(url_file):
            with open(url_file) as f:
                url = f.read().strip()
            print(f"\n✅ 公网链接: {url}")
            found = True
            break
        print(f"  {30-i}秒...", end="\r")

if not found:
    print("未捕获到链接，请检查上方输出")
