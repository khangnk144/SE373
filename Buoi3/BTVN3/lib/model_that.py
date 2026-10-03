# -*- coding: utf-8 -*-
"""BTVN3 · Model thật: API llm.uit.edu.vn (chuẩn OpenAI, chỉ chạy trong mạng nội bộ UIT).

Đọc từ .env:  LLM_API_KEY (bắt buộc) · LLM_MODEL = qwen | gemma · LLM_THINKING = 0 | 1

Server vLLM của UIT chạy không có --enable-auto-tool-choice / --tool-call-parser: gửi tools với
tool_choice auto/required/tên hàm đều bị HTTP 400. Với tool_choice="none", chat template vẫn đưa
tools vào prompt và model vẫn sinh lời gọi tool dạng text thô; ChatUIT tự parse text đó thành
tool_calls của LangChain, nên create_agent và harness chạy như với API có tool calling.
"""
import os
import re
import uuid

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

MODEL_UIT = {
    "qwen": ("https://llm.uit.edu.vn/qwen/v1", "qwen3.8-27b"),
    "gemma": ("https://llm.uit.edu.vn/gemma/v1", "gemma-4-26b"),
}

# Qwen:  <tool_call><function=ten><parameter=k>v</parameter>...</function></tool_call>
QWEN_CALL = re.compile(r"<tool_call>\s*<function=([\w.-]+)>(.*?)</function>\s*</tool_call>", re.S)
QWEN_PARAM = re.compile(r"<parameter=([\w.-]+)>\n?(.*?)\n?</parameter>", re.S)
# Gemma: <|tool_call>call:ten{k:<|"|>v<|"|>,...}<tool_call|>   (cần skip_special_tokens=False)
GEMMA_CALL = re.compile(r"(?:<\|tool_call>)?call:([\w.-]+)\{(.*?)\}(?:<tool_call\|>)?", re.S)
GEMMA_PARAM = re.compile(r'(\w+):(?:<\|"\|>(.*?)<\|"\|>|([^,}]*))', re.S)
GEMMA_KENH = re.compile(r"<\|channel>.*?<channel\|>", re.S)      # khối thought (thường rỗng) của Gemma
TOKEN_DAC_BIET = re.compile(r"<\|[^>]*>|<[a-z_]+\|>")


def tach_tool_call(text: str, ten: str) -> tuple[str, list]:
    """Tách lời gọi tool khỏi text model sinh ra. Trả (phần text còn lại, tool_calls)."""
    if ten == "qwen":
        goi = [(f, {k: v.strip() for k, v in QWEN_PARAM.findall(b)}) for f, b in QWEN_CALL.findall(text)]
        con_lai = QWEN_CALL.sub("", text)
    else:
        goi = [(f, {k: (q if q else r.strip()) for k, q, r in GEMMA_PARAM.findall(b)})
               for f, b in GEMMA_CALL.findall(text)]
        con_lai = GEMMA_CALL.sub("", text)
    con_lai = TOKEN_DAC_BIET.sub("", GEMMA_KENH.sub("", con_lai)).strip()
    return con_lai, [{"name": f, "args": a, "id": f"call_{uuid.uuid4().hex[:12]}", "type": "tool_call"}
                     for f, a in goi]


class ChatUIT(ChatOpenAI):
    """ChatOpenAI gửi tool_choice="none" và tự parse lời gọi tool từ text."""
    ten: str = "qwen"

    def bind_tools(self, tools, *, tool_choice=None, **kw):
        return super().bind_tools(tools, tool_choice="none", **kw)

    def _generate(self, *args, **kw):
        kq = super()._generate(*args, **kw)
        for g in kq.generations:
            m = g.message
            if isinstance(m.content, str):
                con_lai, goi = tach_tool_call(m.content, self.ten)
                if goi or con_lai != m.content:
                    g.message = AIMessage(content=con_lai, tool_calls=goi, id=m.id,
                                          usage_metadata=m.usage_metadata,
                                          response_metadata=m.response_metadata)
        return kq


def model_that(ten: str | None = None):
    load_dotenv()
    ten = ten or os.environ.get("LLM_MODEL", "qwen")
    if not os.environ.get("LLM_API_KEY"):
        raise SystemExit("Chưa có LLM_API_KEY. Copy .env.example thành .env rồi điền key.")
    base_url, model = MODEL_UIT[ten]
    if ten == "qwen":
        # Chế độ suy nghĩ của Qwen bật sẵn và rất chậm (15,8 s so với 1,3 s một câu ngắn).
        bat = os.environ.get("LLM_THINKING", "0") == "1"
        extra = {"chat_template_kwargs": {"enable_thinking": bat}}
    else:
        extra = {"skip_special_tokens": False}      # giữ dấu <|"|> bao chuỗi trong lời gọi tool của Gemma
    return ChatUIT(ten=ten, base_url=base_url, model=model, api_key=os.environ["LLM_API_KEY"],
                   temperature=0, max_tokens=2000, timeout=300, extra_body=extra)
