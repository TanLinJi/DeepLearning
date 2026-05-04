# 图序列判定小程序 — 打包为 Windows EXE

## 已准备的文件

- `../图论图序列判定小程序_standalone.html` — 离线自包含版（Tailwind + 字体已内联，无需网络）

## 方案一：GitHub Actions 自动构建（推荐，免费，不需自己装任何东西）

1. 在 GitHub 创建一个仓库
2. 将整个项目文件夹上传到该仓库
3. GitHub 会自动运行 `.github/workflows/build-exe.yml` 工作流
4. 在仓库页面的 **Actions** 标签页下载生成的 EXE

## 方案二：本机 Windows 运行 nativefier

先安装 Node.js (https://nodejs.org)，然后在 PowerShell 中运行：

```
npm install -g nativefier
cd packaging
nativefier --name "图序列判定" --platform windows --arch x64 --portable ../图论图序列判定小程序_standalone.html ./dist
```

生成的 EXE 在 `./dist/图序列判定-win32-x64/` 目录下。

## 方案三：Python + PyInstaller（体积更小 ~40MB）

先安装 Python (https://python.org)，然后：

```
pip install pywebview pyinstaller
```

创建 `app.py`：
```python
import webview
import os
html_path = os.path.join(os.path.dirname(__file__), "图论图序列判定小程序_standalone.html")
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()
webview.create_window("图序列判定软件", html=html, width=900, height=800)
webview.start()
```

打包：
```
pyinstaller --onefile --windowed --name "图序列判定" app.py
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `图论图序列判定小程序_standalone.html` | 离线自包含 HTML（可直接双击打开使用） |
| `.github/workflows/build-exe.yml` | GitHub Actions 自动构建配置 |
| `build_exe.ps1` | Windows 本地构建脚本 |
