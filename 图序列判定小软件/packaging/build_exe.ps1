# Windows EXE 打包脚本（需在 Windows 机器上运行）

# 方案一：nativefier（最简单，一行命令）
# 先安装 Node.js (https://nodejs.org)，然后：
npm install -g nativefier
nativefier --name "图序列判定" --platform windows --arch x64 --portable ../图论图序列判定小程序_standalone.html ./dist

Write-Host "EXE 已生成在 .\dist\图序列判定-win32-x64\ 目录下"
