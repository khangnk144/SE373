"""Chạy một cuộc trò chuyện với app.py thật của một stage (model thật) và lưu đầy đủ bằng chứng.

Dùng Streamlit AppTest (cách test của lab) để chạy đúng app.py: mỗi lần chạy script = tải lại trang +
cuộc trò chuyện mới; mỗi prompt = một lượt chat gửi qua ô chat. Trace JSONL do chính app ghi vào
<stage>/traces/. Script lưu thêm vào --out:
  - api-calls.jsonl : mọi HTTP request/response tới provider (body đầy đủ, KHÔNG ghi header/API key)
  - conversation.json: Conversation JSON của app (messages, snapshots, events) + câu trả lời từng lượt
  - transcript.md    : bản đọc nhanh: prompt, tool call + kết quả, câu trả lời, file trace tương ứng
  - traces/, output/ : bản sao trace và file output mới sinh ra trong lần chạy này

Credential đọc từ file .env bên ngoài (--env), chỉ đặt vào biến môi trường của tiến trình này.

Ví dụ (từ thư mục BTVN4):
  python run-scenario.py --stage block1/stage-02-skills --out block1/evidence/stage-02/case-a "Tôi mua ..."
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import dotenv_values
from streamlit.testing.v1 import AppTest

DEFAULT_ENV = Path(__file__).resolve().parent.parent / "agent-tools-skills-lab" / "stage-00-chat" / ".env"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--stage", required=True, help="Thư mục stage, ví dụ block1/stage-02-skills")
    parser.add_argument("--out", required=True, help="Thư mục lưu bằng chứng của kịch bản")
    parser.add_argument("--env", default=str(DEFAULT_ENV), help="File .env chứa OPENAI_API_KEY, MODEL_NAME, OPENAI_BASE_URL")
    parser.add_argument("--pause", type=float, default=3.0, help="Số giây nghỉ giữa các lượt (tránh rate limit)")
    parser.add_argument("prompts", nargs="+", help="Các lượt chat, theo thứ tự, trong CÙNG một cuộc trò chuyện")
    return parser.parse_args()


def body_json(raw: bytes):
    try:
        return json.loads(raw.decode("utf-8")) if raw else None
    except (UnicodeDecodeError, ValueError):
        return raw.decode("utf-8", errors="replace")


def make_api_logger(log_path: Path):
    def log_response(response: httpx.Response) -> None:
        response.read()
        request = response.request
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "elapsed_ms": round(response.elapsed.total_seconds() * 1000, 1),
            "request_body": body_json(request.content),
            "response_body": body_json(response.content),
        }
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return log_response


def snapshot_files(folder: Path) -> dict[Path, float]:
    return {p: p.stat().st_mtime for p in folder.rglob("*") if p.is_file()} if folder.is_dir() else {}


def render_content(text) -> str:
    if not isinstance(text, str):
        return json.dumps(text, ensure_ascii=False, indent=2)
    try:
        return json.dumps(json.loads(text), ensure_ascii=False, indent=2)
    except ValueError:
        return text


def write_transcript(path: Path, stage: str, model: str, turns: list[dict], messages: list[dict], traces: list[str]) -> None:
    lines = [f"# Transcript: {path.parent.name}", "", f"- Stage: `{stage}`", f"- Model: `{model}`",
             f"- Trace (thứ tự lượt): {', '.join(f'`{t}`' for t in traces) or '(không có)'}", ""]
    turn_no = 0
    for message in messages:
        role = message.get("role")
        if role == "user":
            turn_no += 1
            turn = turns[turn_no - 1] if turn_no <= len(turns) else {}
            lines += [f"## Lượt {turn_no}", "", "**Người dùng:**", "", "```text", message.get("content", ""), "```", ""]
            if turn.get("error"):
                lines += [f"**LỖI:** `{turn['error']}`", ""]
        elif role == "assistant" and message.get("tool_calls"):
            for call in message["tool_calls"]:
                lines += [f"**Tool call** `{call['name']}` (id `{call['id']}`):", "", "```json",
                          json.dumps(call.get("args", {}), ensure_ascii=False, indent=2), "```", ""]
            if message.get("content"):
                lines += ["Kèm text:", "", "```text", str(message["content"]), "```", ""]
        elif role == "tool":
            lines += [f"**Tool result** `{message.get('name')}` (id `{message.get('tool_call_id')}`):", "", "```json",
                      render_content(message.get("content")), "```", ""]
        elif role == "assistant":
            lines += ["**Agent trả lời:**", "", str(message.get("content", "")), ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    stage = Path(args.stage).resolve()
    out = Path(args.out).resolve()
    if out.exists():
        print(f"{out} đã tồn tại; xóa hoặc đổi --out để không trộn bằng chứng của hai lần chạy.", file=sys.stderr)
        return 1
    out.mkdir(parents=True)

    env = dotenv_values(args.env)
    for key in ("OPENAI_API_KEY", "MODEL_NAME", "OPENAI_BASE_URL"):
        if env.get(key):
            os.environ[key] = env[key]
    os.chdir(stage)
    sys.path.insert(0, str(stage))
    import agent  # noqa: E402 (module của stage, sau khi thêm stage vào sys.path)
    import paths  # noqa: E402
    from langchain_openai import ChatOpenAI  # noqa: E402

    api_log = out / "api-calls.jsonl"

    def build_model_with_api_log(settings):
        """Giống agent.build_model, chỉ thêm http_client có hook ghi request/response."""
        kwargs = {"model": settings.model_name, "api_key": settings.api_key,
                  "http_client": httpx.Client(timeout=300, event_hooks={"response": [make_api_logger(api_log)]})}
        if settings.base_url:
            kwargs["base_url"] = settings.base_url
        return ChatOpenAI(**kwargs)

    agent.build_model = build_model_with_api_log
    traces_before = set(paths.TRACES_DIR.glob("*.jsonl"))
    workspace = getattr(paths, "WORKSPACE_DIR", None)  # stage 00 không có workspace
    output_dir = workspace / paths.OUTPUT_SUBDIR if workspace else stage / "__no_workspace__"
    outputs_before = snapshot_files(output_dir)

    at = AppTest.from_file(str(stage / "app.py"), default_timeout=900).run()
    if at.exception or at.chat_input[0].disabled:
        print(f"App không sẵn sàng: {at.exception or 'thiếu cấu hình model'}", file=sys.stderr)
        return 1
    for index, prompt in enumerate(args.prompts):
        if index:
            time.sleep(args.pause)
        print(f"[lượt {index + 1}] {prompt}", flush=True)
        at.chat_input[0].set_value(prompt).run()
        if at.exception:
            print(f"Exception của app: {at.exception}", file=sys.stderr)
            return 1
        turn = at.session_state["ui_history"][-1]
        print(f"  -> {turn['error'] or turn['answer'][:300]}", flush=True)

    observer = at.session_state["observer"]
    turns = [{k: t[k] for k in ("chat_turn", "run_id", "user", "answer", "error")} for t in at.session_state["ui_history"]]
    traces = sorted(set(paths.TRACES_DIR.glob("*.jsonl")) - traces_before)
    (out / "traces").mkdir()
    for trace in traces:
        shutil.copy2(trace, out / "traces" / trace.name)
    for file, mtime in snapshot_files(output_dir).items():
        if outputs_before.get(file) != mtime:
            target = out / "output" / file.relative_to(output_dir)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, target)

    model = os.environ.get("MODEL_NAME", "")
    conversation = {"stage": stage.name, "model": model, "base_url": os.environ.get("OPENAI_BASE_URL"),
                    "trace_files": [t.name for t in traces], "turns": turns, "observer_export": observer.export()}
    (out / "conversation.json").write_text(json.dumps(conversation, ensure_ascii=False, indent=2), encoding="utf-8")
    write_transcript(out / "transcript.md", stage.name, model, turns, observer.messages, [t.name for t in traces])
    print(f"Đã lưu bằng chứng vào {out}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
