# -*- coding: utf-8 -*-
"""BTVN3 · Mẫu 1 · ReAct.

Suy luận → hành động → quan sát → suy luận tiếp, cho tới khi model thôi gọi tool.
Không có kế hoạch trước; mỗi vòng model tự chọn bước kế tiếp từ observation.
Harness cắm vào vòng lặp qua HarnessMiddleware.

    python agent_react.py --kich-ban het_cho
    python agent_react.py --kich-ban can_duyet --that qwen
"""
from langchain.agents import create_agent

from lib.chay import cli
from lib.harness import Harness, HarnessMiddleware
from lib.rang_buoc import mo_ta_yeu_cau, prompt_he_thong
from lib.tools_dat_ve import tools_langchain


def chay(model, h: Harness) -> str:
    agent = create_agent(model=model, tools=tools_langchain(h.hk),
                         system_prompt=prompt_he_thong(), middleware=[HarnessMiddleware(h)])
    kq = agent.invoke({"messages": [{"role": "user", "content": mo_ta_yeu_cau()}]},
                      {"recursion_limit": 100})     # trần cứng cuối cùng; ngân sách của harness chặn trước
    return kq["messages"][-1].content


if __name__ == "__main__":
    cli("ReAct", chay)
