"""Gọi trực tiếp tool list_files của một stage (đúng cách agent gọi: tool.invoke -> JSON string) và lưu kết quả.

Các trường hợp: thư mục hợp lệ, đường dẫn file, đường dẫn không tồn tại, đường dẫn vượt workspace
(.., absolute) và junction trỏ ra ngoài workspace (Windows; thay cho symlink vì symlink cần Developer Mode).
Chỉ dùng dữ liệu giả: đích của junction là thư mục tạm chứa một file giả.

Chạy từ thư mục BTVN4:
  python block1/check-list-files-tool.py block1/stage-01-files block1/evidence/00-list-files-direct-check
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    stage, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    sys.path.insert(0, str(stage))
    import paths  # noqa: E402 (module của stage)
    from tools import list_files  # noqa: E402

    workspace = paths.WORKSPACE_DIR.resolve()
    first_policy = json.loads(list_files.invoke({"path": "data/policies"}))["entries"][0]["path"]
    cases = [
        ("Thư mục hợp lệ", "data/policies", True),
        ("Thư mục gốc workspace", ".", True),
        ("Đường dẫn là file", first_policy, False),
        ("Đường dẫn không tồn tại", "data/khong-ton-tai", False),
        ("Vượt workspace bằng ..", "..", False),
        ("Vượt workspace bằng data/../..", "data/../..", False),
        ("Đường dẫn tuyệt đối", str(workspace / "data"), False),
    ]

    fake_outside = Path(tempfile.mkdtemp(prefix="fake-outside-"))
    (fake_outside / "fake-secret.txt").write_text("dữ liệu giả", encoding="utf-8")
    junction = workspace / "data" / "junction-ra-ngoai"
    made = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(fake_outside)], capture_output=True).returncode == 0
    if made:
        cases.append(("Junction trỏ ra ngoài workspace", "data/junction-ra-ngoai", False))
        cases.append(("Liệt kê thư mục chứa junction (junction phải bị ẩn)", "data", True))

    results = []
    try:
        for name, path, expect_ok in cases:
            raw = list_files.invoke({"path": path})
            result = json.loads(raw)
            passed = result["ok"] is expect_ok
            if made and path == "data":
                passed = passed and all(e["name"] != junction.name for e in result["entries"])
            results.append({"case": name, "path": path, "expected_ok": expect_ok, "passed": passed, "raw_tool_result": raw})
    finally:
        if junction.exists() or junction.is_junction():
            junction.rmdir()  # chỉ xóa junction, không xóa đích

    out.mkdir(parents=True, exist_ok=True)
    (out / f"{stage.name}.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [f"# Kiểm tra trực tiếp list_files: `{stage.name}`", "",
             "| # | Trường hợp | path | Mong đợi | Kết quả | Đạt |", "|---|---|---|---|---|---|"]
    for i, r in enumerate(results, 1):
        data = json.loads(r["raw_tool_result"])
        got = f"ok, {len(data['entries'])} mục" if data["ok"] else f"lỗi `{data['error']['code']}`"
        lines.append(f"| {i} | {r['case']} | `{r['path']}` | {'ok' if r['expected_ok'] else 'lỗi'} | {got} | {'✅' if r['passed'] else '❌'} |")
    lines += ["", "Tool result đầy đủ (JSON string tool trả cho model):", ""]
    for r in results:
        lines += [f"**{r['case']}** (`{r['path']}`)", "", "```json", r["raw_tool_result"], "```", ""]
    (out / f"{stage.name}.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:len(results) + 4]))
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
