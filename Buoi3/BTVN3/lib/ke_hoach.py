# -*- coding: utf-8 -*-
"""BTVN3 · Khối dựng chung cho Plan-then-Execute và mẫu Lai.

    lap_ke_hoach       gọi model MỘT lần, sinh trọn kế hoạch (danh sách bước)
    thuc_thi_buoc      một sub-agent ReAct nhỏ làm đúng một bước, có harness
    ke_hoach_lech      code quyết định observation có lệch kế hoạch không (không tốn model)
    lap_lai_ke_hoach   gọi model lập lại các bước còn lại từ trạng thái hiện tại
"""
import json
import re

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage

from lib.harness import Harness, HarnessMiddleware
from lib.rang_buoc import YEU_CAU, prompt_he_thong
from lib.tools_dat_ve import TEN_TOOL, tools_langchain

LAP_KE_HOACH = "[LAP_KE_HOACH]"
LAP_LAI = "[LAP_LAI_KE_HOACH]"
BUOC = "[BUOC]"

_DINH_DANG = ("Mỗi bước bắt đầu bằng đúng tên một tool (" + ", ".join(TEN_TOOL) + ") rồi mô tả ngắn. "
              'Chỉ trả về JSON, không giải thích: {"ke_hoach": ["search_flights ...", "..."]}')

PROMPT_THUC_THI = (prompt_he_thong() + "\nBạn là bộ THỰC THI: chỉ làm đúng bước trong tin nhắn "
                   f"{BUOC} cuối cùng, gọi tool cần cho bước đó, tóm tắt kết quả trong một câu rồi dừng. "
                   "Không tự làm sang bước khác.")


def doc_json(text: str) -> dict:
    """Lấy object JSON đầu tiên trong câu trả lời (model hay bọc thêm ```json ... ```)."""
    m = re.search(r"\{.*\}", str(text), re.DOTALL)
    if not m:
        raise ValueError(f"không thấy JSON trong: {str(text)[:120]!r}")
    return json.loads(m.group(0))


def nhat_ky(messages) -> list:
    """Ghép tool_call của AI với ToolMessage tương ứng: [{"tool", "args", "ket_qua"}]."""
    goi = {c["id"]: c for m in messages if m.type == "ai" for c in (getattr(m, "tool_calls", None) or [])}
    ra = []
    for m in messages:
        if m.type == "tool" and m.tool_call_id in goi:
            try:
                kq = json.loads(m.content)
            except (TypeError, ValueError):
                kq = {"status": "raw", "content": str(m.content)}
            ra.append({"tool": goi[m.tool_call_id]["name"], "args": goi[m.tool_call_id]["args"], "ket_qua": kq})
    return ra


def _goi_ke_hoach(model, h: Harness, noi_dung: str) -> list:
    ai = model.invoke([SystemMessage(prompt_he_thong()), HumanMessage(noi_dung)])
    h.ghi_goi_model(ai)
    try:
        return [str(b) for b in doc_json(ai.content)["ke_hoach"]]
    except (ValueError, KeyError, TypeError) as e:
        h.dung("LỖI KẾ HOẠCH", f"model không trả kế hoạch đúng định dạng: {e}",
               "Chạy lại, hay đổi sang mẫu ReAct cho yêu cầu này?")
        return []


def lap_ke_hoach(model, h: Harness) -> list:
    return _goi_ke_hoach(model, h, f"{LAP_KE_HOACH}\nLập TRỌN kế hoạch trước khi làm. {_DINH_DANG}")


def lap_lai_ke_hoach(model, h: Harness, lich_su) -> list:
    dong = "\n".join(json.dumps(x, ensure_ascii=False) for x in nhat_ky(lich_su))
    return _goi_ke_hoach(model, h, (
        f"{LAP_LAI}\nKết quả vừa rồi lệch kế hoạch. Nhật ký tool đã chạy:\n{dong}\n"
        "Lập lại các bước CÒN LẠI tính từ trạng thái hiện tại. Nếu không còn cách nào thoả "
        f'ràng buộc thì trả {{"ke_hoach": []}}. {_DINH_DANG}'))


def thuc_thi_buoc(model, h: Harness, buoc: str, lich_su: list) -> list:
    executor = create_agent(model=model, tools=tools_langchain(h.hk),
                            system_prompt=PROMPT_THUC_THI, middleware=[HarnessMiddleware(h)])
    kq = executor.invoke({"messages": lich_su + [HumanMessage(f"{BUOC} {buoc}")]},
                         {"recursion_limit": 25})
    return kq["messages"]


def ke_hoach_lech(nk_buoc: list) -> bool:
    """Observation của bước vừa làm có đổi đáng kể không. Kiểm bằng code, không tốn model."""
    if not nk_buoc:
        return True                      # bước không gọi được tool nào
    for x in nk_buoc:
        kq = x["ket_qua"]
        if kq.get("status") != "ok":
            return True
        if x["tool"] == "check_seat" and (kq["seats_left"] <= 0 or kq["price"] > YEU_CAU["tran_gia"]):
            return True
    return False
