"""Bash tool: chạy `bash -c` đồng bộ trong workspace, timeout ngắn, env tối thiểu.

Giới hạn: cwd và env tối thiểu KHÔNG phải sandbox. Lệnh bash vẫn có thể đọc/ghi ngoài workspace
với quyền của user đang chạy app. Chỉ dùng trong môi trường lab với dữ liệu giả.

Windows: `bash` mặc định là launcher WSL trong System32 (không dùng được khi máy không có distro Linux),
nên dùng Git Bash. Trên POSIX hành vi không đổi.
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
from pathlib import Path

from langchain_core.tools import tool

import paths

DEFAULT_TIMEOUT_SECONDS = 10
MAX_OUTPUT_CHARS = 20_000
SYSTEM_PATH = "/usr/local/bin:/usr/bin:/bin"
IS_WINDOWS = os.name == "nt"
KILL_WAIT_SECONDS = 2


def find_bash() -> str:
    """POSIX: `bash` trong PATH. Windows: bash.exe của Git for Windows."""
    if not IS_WINDOWS:
        return "bash"
    git = shutil.which("git")
    roots = [Path(git).resolve().parents[1]] if git else []
    roots.append(Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Git")
    for root in roots:
        candidate = root / "usr" / "bin" / "bash.exe"
        if candidate.is_file():
            return str(candidate)
    return "bash"


BASH = find_bash()


def minimal_env(workspace: Path) -> dict[str, str]:
    """PATH trỏ venv của project trước, locale UTF-8. Không truyền API key hay biến môi trường khác."""
    venv_bin = str(Path(sys.executable).parent)
    locale = os.environ.get("LANG", "")
    env = {
        "PATH": f"{venv_bin}:{SYSTEM_PATH}",
        "HOME": str(workspace),
        "LANG": locale if "UTF-8" in locale.upper() else "C.UTF-8",
        "LC_ALL": locale if "UTF-8" in locale.upper() else "C.UTF-8",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    if IS_WINDOWS:
        # Git Bash tự đổi PATH dạng Windows (phân cách ;) sang POSIX; Python trên Windows cần SYSTEMROOT để khởi động.
        bash_dirs = [str(Path(BASH).parent)] if Path(BASH).is_absolute() else []  # không đưa "." (workspace) vào PATH
        env["PATH"] = os.pathsep.join([venv_bin, *bash_dirs])
        env["SYSTEMROOT"] = os.environ.get("SYSTEMROOT", r"C:\Windows")
    return env


def _kill(process: subprocess.Popen) -> None:
    if IS_WINDOWS:  # không có process group; taskkill /T dừng cả cây tiến trình con
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], capture_output=True)
    else:
        os.killpg(process.pid, signal.SIGKILL)


def _clip(text: str) -> tuple[str, bool]:
    if len(text) <= MAX_OUTPUT_CHARS:
        return text, False
    return text[:MAX_OUTPUT_CHARS] + f"\n…[đã cắt, tổng {len(text)} ký tự]", True


def _run_bash(command: str, workspace: Path, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> dict:
    if not command.strip():
        return {"ok": False, "exit_code": None, "stdout": "", "stderr": "", "timed_out": False,
                "error": {"code": "EMPTY_COMMAND", "message": "Command rỗng."}}
    process = subprocess.Popen(
        [BASH, "-c", command],  # không login shell, không đọc profile
        cwd=workspace,
        env=minimal_env(workspace),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        start_new_session=True,  # để kill cả process group khi timeout
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        _kill(process)
        if IS_WINDOWS:
            try:
                stdout, stderr = process.communicate(timeout=KILL_WAIT_SECONDS)
            except subprocess.TimeoutExpired:  # tiến trình MSYS con (ví dụ sleep) có thể còn giữ pipe
                stdout, stderr = "", ""
        else:
            stdout, stderr = process.communicate()
        stdout, out_clipped = _clip(stdout or "")
        stderr, err_clipped = _clip(stderr or "")
        return {
            "ok": False,
            "exit_code": None,
            "stdout": stdout,
            "stderr": stderr,
            "timed_out": True,
            "truncated": out_clipped or err_clipped,
            "error": {"code": "TIMEOUT", "message": f"Command chạy quá {timeout} giây, đã dừng. stdout/stderr là output một phần."},
        }
    stdout, out_clipped = _clip(stdout)
    stderr, err_clipped = _clip(stderr)
    return {
        "ok": True,
        "exit_code": process.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "timed_out": False,
        "truncated": out_clipped or err_clipped,
    }


@tool
def bash(command: str) -> str:
    """Chạy một lệnh bash ngắn (bash -c) trong thư mục workspace và trả về JSON.

    cwd là workspace, nên dùng đường dẫn tương đối như data/tasks.csv. `python` là Python của project.
    Timeout 10 giây; không chạy tiến trình nền hay lệnh tương tác.
    Kết quả: {"ok": true, "exit_code": 0, "stdout": "...", "stderr": "", "timed_out": false}.
    ok=true nghĩa là lệnh đã chạy xong và có kết quả; exit_code khác 0 nghĩa là chương trình báo lỗi.
    Timeout: {"ok": false, "exit_code": null, "timed_out": true, ...} kèm output một phần nếu có.
    """
    return json.dumps(_run_bash(command, paths.WORKSPACE_DIR), ensure_ascii=False)
