"""Chạy trực tiếp script check_csv.py của stage 04 (không qua agent) và lưu stdout/stderr/exit code.

Tương đương lệnh trong đề, chạy từ thư mục stage 04:
  uv run python workspace/skills/csv-quality/scripts/check_csv.py --input workspace/data/workload.csv --max-hours 8
(ở đây dùng Python của .venv lab thay cho `uv run`; PYTHONIOENCODING=utf-8 giống bash tool của app.)

Chạy từ thư mục BTVN4:
  python block2/run-check-csv-direct.py block2/stage-04-script-skill block2/evidence/00-check-csv-direct
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = "workspace/skills/csv-quality/scripts/check_csv.py"
CASES = [
    ("threshold-8", "CSV đề bài, ngưỡng 8", ["--input", "workspace/data/workload.csv", "--max-hours", "8"]),
    ("threshold-9", "CSV đề bài, ngưỡng 9", ["--input", "workspace/data/workload.csv", "--max-hours", "9"]),
    ("edge-threshold-0", "Trường hợp đặc biệt: ID đầu tiên có hours không hợp lệ, ngưỡng 0",
     ["--input", "workspace/data/workload-edge.csv", "--max-hours", "0"]),
    ("missing-file", "File không tồn tại", ["--input", "workspace/data/khong-ton-tai.csv", "--max-hours", "8"]),
    ("missing-max-hours", "Thiếu --max-hours", ["--input", "workspace/data/workload.csv"]),
    ("invalid-max-hours", "--max-hours không hợp lệ (-1)", ["--input", "workspace/data/workload.csv", "--max-hours", "-1"]),
]


def main() -> int:
    stage, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    inputs = {p: p.read_bytes() for p in (stage / "workspace" / "data").glob("workload*.csv")}
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    summary = ["# Chạy trực tiếp check_csv.py", "", f"Thư mục chạy: `{stage.name}`", "",
               "| Trường hợp | Lệnh | Exit | Kết quả chính |", "|---|---|---|---|"]
    for key, title, args in CASES:
        result = subprocess.run([sys.executable, SCRIPT, *args], cwd=stage, env=env, capture_output=True,
                                text=True, encoding="utf-8", timeout=30)
        command = " ".join(["python", SCRIPT, *args])
        record = {"case": title, "command": command, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
        (out / f"{key}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        if result.returncode == 0:
            (out / f"{key}.stdout.json").write_text(result.stdout, encoding="utf-8")
            data = json.loads(result.stdout)
            excluded = ", ".join(f"dòng {r['line']}: {'+'.join(r['reasons'])}" for r in data["excluded_rows"])
            main_result = (f"hours_by_owner={json.dumps(data['hours_by_owner'], ensure_ascii=False)}; "
                           f"overloaded={[o['owner'] for o in data['overloaded_owners']]}; loại: {excluded}")
        else:
            main_result = "stderr: " + result.stderr.strip().splitlines()[-1]
        summary.append(f"| {title} | `{command}` | {result.returncode} | {main_result} |")
    unchanged = all(p.read_bytes() == before for p, before in inputs.items())
    summary += ["", f"CSV đầu vào không bị sửa sau khi chạy: {'có' if unchanged else 'KHÔNG'} ({', '.join(p.name for p in inputs)})"]
    (out / "README.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))
    return 0 if unchanged else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
