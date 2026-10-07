"""Proxy OpenAI-compatible cục bộ: thêm bước parse tool call mà server llm.uit.edu.vn chưa bật.

Server vLLM của UIT chạy không có --enable-auto-tool-choice / --tool-call-parser: request có tools với
tool_choice auto bị HTTP 400. Với tool_choice="none", chat template vẫn đưa tools vào prompt và Qwen vẫn
sinh lời gọi tool dạng text:
    <tool_call><function=ten><parameter=k>v</parameter>...</function></tool_call>
Proxy làm đúng việc của tool-call parser phía server:
    request : giữ nguyên, chỉ đổi tool_choice -> "none" khi có tools; tắt chế độ suy nghĩ của Qwen (trừ khi --thinking)
    response: tách text <tool_call> thành message.tool_calls chuẩn OpenAI, finish_reason = "tool_calls"
Model vẫn tự quyết định gọi tool nào với tham số gì; proxy không thêm/bớt/sửa lời gọi. Text gốc của model
được giữ trong choices[i].x_uit_proxy.raw_content để đối chiếu.

API key không nằm trong proxy: header Authorization của client (OPENAI_API_KEY trong .env) được chuyển tiếp.

Chạy (cần mạng nội bộ UIT):
    python uit-tool-call-proxy.py --port 8787
Cấu hình .env của stage:
    OPENAI_API_KEY=<key llm.uit.edu.vn>
    MODEL_NAME=qwen3.8-27b
    OPENAI_BASE_URL=http://127.0.0.1:8787/v1
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx

UPSTREAM = "https://llm.uit.edu.vn/qwen/v1"
QWEN_CALL = re.compile(r"<tool_call>\s*<function=([\w.-]+)>(.*?)</function>\s*</tool_call>", re.S)
QWEN_PARAM = re.compile(r"<parameter=([\w.-]+)>\n?(.*?)\n?</parameter>", re.S)


def parse_tool_calls(text: str) -> tuple[str, list[dict]]:
    """Tách lời gọi tool dạng text của Qwen. Trả (phần text còn lại, tool_calls chuẩn OpenAI)."""
    calls = [
        {
            "id": f"call_{uuid.uuid4().hex[:12]}",
            "type": "function",
            "function": {"name": name, "arguments": json.dumps(dict(QWEN_PARAM.findall(body)), ensure_ascii=False)},
        }
        for name, body in QWEN_CALL.findall(text)
    ]
    return QWEN_CALL.sub("", text).strip(), calls


def convert_request(body: dict, thinking: bool) -> dict:
    body = dict(body)
    if body.get("tools"):
        body["tool_choice"] = "none"  # server UIT chỉ nhận "none"; tools vẫn được render vào prompt
        body.pop("parallel_tool_calls", None)
    kwargs = dict(body.get("chat_template_kwargs") or {})
    kwargs.setdefault("enable_thinking", thinking)
    body["chat_template_kwargs"] = kwargs
    return body


def convert_response(data: dict) -> dict:
    for choice in data.get("choices", []):
        message = choice.get("message") or {}
        raw = message.get("content")
        if not isinstance(raw, str) or message.get("tool_calls"):
            continue
        rest, calls = parse_tool_calls(raw)
        choice["x_uit_proxy"] = {"raw_content": raw, "parsed_tool_calls": len(calls)}
        if calls:
            message["tool_calls"] = calls
            message["content"] = rest or None
            choice["finish_reason"] = "tool_calls"
    return data


class Handler(BaseHTTPRequestHandler):
    upstream: str = UPSTREAM
    thinking: bool = False
    client = httpx.Client(timeout=600)

    def _send(self, status: int, payload: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _error(self, status: int, message: str) -> None:
        self._send(status, json.dumps({"error": {"message": message, "type": "uit_proxy_error"}}, ensure_ascii=False).encode())

    def do_POST(self) -> None:  # noqa: N802 (tên method của BaseHTTPRequestHandler)
        if not self.path.rstrip("/").endswith("/chat/completions"):
            return self._error(404, f"Proxy chỉ hỗ trợ /v1/chat/completions, nhận {self.path}")
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        except ValueError:
            return self._error(400, "Body không phải JSON")
        if body.get("stream"):
            return self._error(400, "Proxy không hỗ trợ stream=true")
        headers = {"Authorization": self.headers.get("Authorization", ""), "Content-Type": "application/json"}
        try:
            upstream = self.client.post(f"{self.upstream}/chat/completions", json=convert_request(body, self.thinking), headers=headers)
        except httpx.HTTPError as exc:
            return self._error(502, f"Không gọi được {self.upstream}: {type(exc).__name__}: {exc}")
        if upstream.status_code != 200:
            return self._send(upstream.status_code, upstream.content)  # lỗi của server UIT trả nguyên văn
        self._send(200, json.dumps(convert_response(upstream.json()), ensure_ascii=False).encode("utf-8"))

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"[uit-proxy] {self.address_string()} {fmt % args}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Proxy thêm tool-call parser cho llm.uit.edu.vn (Qwen).")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--upstream", default=UPSTREAM)
    parser.add_argument("--thinking", action="store_true", help="Bật chế độ suy nghĩ của Qwen (chậm hơn nhiều)")
    args = parser.parse_args()
    Handler.upstream, Handler.thinking = args.upstream.rstrip("/"), args.thinking
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"UIT tool-call proxy: http://127.0.0.1:{args.port}/v1 -> {Handler.upstream} (thinking={args.thinking})", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
