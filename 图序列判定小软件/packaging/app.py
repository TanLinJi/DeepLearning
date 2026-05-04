"""图序列判定软件 — Python Webview 打包入口"""
import os
import webview

HTML_FILE = os.path.join(os.path.dirname(__file__), "..", "图论图序列判定小程序_standalone.html")

with open(HTML_FILE, "r", encoding="utf-8") as f:
    html_content = f.read()

webview.create_window(
    title="图序列判定软件",
    html=html_content,
    width=900,
    height=800,
    resizable=True,
)
webview.start()
