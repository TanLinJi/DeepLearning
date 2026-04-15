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
