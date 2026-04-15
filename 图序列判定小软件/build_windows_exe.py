#!/usr/bin/env python3

from __future__ import annotations

import shlex
import shutil
import subprocess
import sys
import textwrap
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_HTML = ROOT / "图论图序列判定小程序.html"
SOURCE_ICON = ROOT / "jtl.ico"

BUILD_DIR = ROOT / "_windows_build"
HTML_CACHE = BUILD_DIR / "ui_offline.html"
TAILWIND_CACHE = BUILD_DIR / "tailwindcdn.js"
DIST_EXE = ROOT / "图序列判定软件.exe"

TAILWIND_URL = "https://cdn.tailwindcss.com"
TAILWIND_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


def run(cmd: list[str], cwd: Path | None = None) -> None:
    printable = " ".join(shlex.quote(part) for part in cmd)
    print(f"+ {printable}")
    subprocess.run(cmd, cwd=cwd, check=True)


def which_any(names: list[str]) -> str:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit(f"Missing required tool: one of {', '.join(names)}")


def load_tailwind() -> str:
    if TAILWIND_CACHE.exists():
        return TAILWIND_CACHE.read_text(encoding="utf-8")

    request = urllib.request.Request(TAILWIND_URL, headers={"User-Agent": TAILWIND_UA})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()

    script_text = data.decode("utf-8")
    script_text = script_text.replace("</script>", "<\\/script>")
    TAILWIND_CACHE.write_text(script_text, encoding="utf-8")
    return script_text


def build_offline_html() -> Path:
    if not SOURCE_HTML.exists():
        raise SystemExit(f"Source HTML not found: {SOURCE_HTML}")

    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    html_text = SOURCE_HTML.read_text(encoding="utf-8")
    html_text = html_text.replace(
        "        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap');\n",
        "",
    )
    html_text = html_text.replace(
        "font-family: 'Noto Sans SC', system-ui, sans-serif;",
        "font-family: 'Microsoft YaHei', 'Noto Sans SC', system-ui, sans-serif;",
    )
    html_text = html_text.replace(
        '<script src="https://cdn.tailwindcss.com"></script>',
        f"<script>{load_tailwind()}</script>",
    )

    HTML_CACHE.write_text(html_text, encoding="utf-8")
    return HTML_CACHE


def prepare_build_sources() -> tuple[Path, Path, Path]:
    build_html = build_offline_html()
    if not SOURCE_ICON.exists():
        raise SystemExit(f"Icon not found: {SOURCE_ICON}")

    build_icon = BUILD_DIR / "app.ico"
    shutil.copy2(SOURCE_ICON, build_icon)

    launcher_c = BUILD_DIR / "launcher.c"
    launcher_rc = BUILD_DIR / "launcher.rc"

    launcher_c.write_text(
        textwrap.dedent(
            r'''
            #include <windows.h>
            #include <shellapi.h>
            #include <wchar.h>

            #define IDR_HTML 101

            static void show_error(const wchar_t *message) {
                MessageBoxW(NULL, message, L"图序列判定软件", MB_OK | MB_ICONERROR);
            }

            static BOOL write_resource_to_file(const wchar_t *path) {
                HRSRC resource_handle = FindResourceW(NULL, MAKEINTRESOURCEW(IDR_HTML), RT_RCDATA);
                if (!resource_handle) {
                    show_error(L"未找到内置 HTML 资源。\n");
                    return FALSE;
                }

                HGLOBAL resource_block = LoadResource(NULL, resource_handle);
                if (!resource_block) {
                    show_error(L"加载 HTML 资源失败。\n");
                    return FALSE;
                }

                DWORD resource_size = SizeofResource(NULL, resource_handle);
                const void *resource_data = LockResource(resource_block);
                if (!resource_data || resource_size == 0) {
                    show_error(L"读取 HTML 资源失败。\n");
                    return FALSE;
                }

                HANDLE file_handle = CreateFileW(
                    path,
                    GENERIC_WRITE,
                    0,
                    NULL,
                    CREATE_ALWAYS,
                    FILE_ATTRIBUTE_NORMAL,
                    NULL
                );
                if (file_handle == INVALID_HANDLE_VALUE) {
                    show_error(L"无法创建临时 HTML 文件。\n");
                    return FALSE;
                }

                DWORD total_written = 0;
                BOOL ok = WriteFile(file_handle, resource_data, resource_size, &total_written, NULL);
                CloseHandle(file_handle);
                if (!ok || total_written != resource_size) {
                    show_error(L"写入临时 HTML 文件失败。\n");
                    return FALSE;
                }

                return TRUE;
            }

            static BOOL build_temp_path(wchar_t *buffer, size_t buffer_count) {
                wchar_t temp_dir[MAX_PATH];
                DWORD temp_len = GetTempPathW(MAX_PATH, temp_dir);
                if (temp_len == 0 || temp_len > MAX_PATH - 1) {
                    show_error(L"无法获取临时目录。\n");
                    return FALSE;
                }

                DWORD pid = GetCurrentProcessId();
                DWORD tick = GetTickCount();
                if (swprintf(
                    buffer,
                    buffer_count,
                    L"%sgraph_seq_tool_%lu_%lu.html",
                    temp_dir,
                    (unsigned long)pid,
                    (unsigned long)tick
                ) < 0) {
                    show_error(L"无法生成临时文件路径。\n");
                    return FALSE;
                }

                return TRUE;
            }

            int WINAPI wWinMain(HINSTANCE instance, HINSTANCE prev_instance, PWSTR cmd_line, int show_cmd) {
                (void)instance;
                (void)prev_instance;
                (void)cmd_line;
                (void)show_cmd;

                wchar_t temp_html_path[MAX_PATH];
                if (!build_temp_path(temp_html_path, MAX_PATH)) {
                    return 1;
                }

                if (!write_resource_to_file(temp_html_path)) {
                    return 1;
                }

                HINSTANCE result = ShellExecuteW(NULL, L"open", temp_html_path, NULL, NULL, SW_SHOWNORMAL);
                if ((INT_PTR)result <= 32) {
                    show_error(L"启动浏览器失败。\n");
                    return 1;
                }

                return 0;
            }
            '''
        ).strip()
        + "\n",
        encoding="utf-8",
    )

    launcher_rc.write_text(
        '1 ICON "app.ico"\n101 RCDATA "ui_offline.html"\n',
        encoding="utf-8",
    )

    return launcher_c, launcher_rc, build_html


def compile_windows_exe() -> Path:
    gcc = which_any(["x86_64-w64-mingw32-gcc"])
    windres = which_any(["x86_64-w64-mingw32-windres"])

    launcher_c, launcher_rc, _ = prepare_build_sources()
    resource_obj = BUILD_DIR / "launcher_res.o"
    intermediate_exe = BUILD_DIR / "graph_seq_tool.exe"

    run([windres, "-O", "coff", str(launcher_rc), "-o", str(resource_obj)], cwd=BUILD_DIR)
    run(
        [
            gcc,
            "-static",
            "-static-libgcc",
            "-municode",
            "-mwindows",
            "-Os",
            "-s",
            str(launcher_c),
            str(resource_obj),
            "-o",
            str(intermediate_exe),
            "-lshell32",
            "-luser32",
        ],
        cwd=BUILD_DIR,
    )

    shutil.copy2(intermediate_exe, DIST_EXE)
    return DIST_EXE


def main() -> int:
    try:
        output = compile_windows_exe()
    except subprocess.CalledProcessError as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return exc.returncode or 1
    except Exception as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1

    print(f"Built: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())