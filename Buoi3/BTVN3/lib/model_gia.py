# -*- coding: utf-8 -*-
"""BTVN3 · Model giả lập để chạy khi KHÔNG ở mạng nội bộ UIT.

Đây KHÔNG phải LLM: nó là một chính sách viết tay, đọc observation trong
messages rồi quyết định bước kế tiếp. Mục đích duy nhất là kiểm tra dây nối
của ba mẫu và của harness. Số liệu đánh giá chạy bằng model này là KỊCH BẢN,
không phải bằng chứng hiệu quả; muốn đánh giá thật phải chạy với --that.

Nó đóng ba vai, nhận ra vai qua dấu ở tin nhắn Human cuối cùng:
    [LAP_KE_HOACH]       trả kế hoạch cố định 5 bước
    [LAP_LAI_KE_HOACH]   lập lại các bước còn lại từ nhật ký
    [BUOC] ...           làm đúng một tool của bước, rồi tóm tắt
    (không có dấu)       ReAct: tự chọn hành động kế tiếp tới khi xong
Khi gặp tool timeout, nó thử lại cùng tham số một cách ngây thơ (để harness bắt lặp).
"""
from __future__ import annotations

import json
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from lib.ke_hoach import BUOC, LAP_KE_HOACH, LAP_LAI, nhat_ky
from lib.rang_buoc import YEU_CAU, vnd
from lib.tools_dat_ve import TEN_TOOL

KE_HOACH_CO_DINH = ["search_flights SGN→DAD ngày 07/10", "check_seat chuyến buổi sáng rẻ nhất",
                    "book_seat chuyến vừa kiểm", "pay booking vừa giữ", "get_booking để xác nhận"]
MO_TA_BUOC = dict(zip(TEN_TOOL, ["search_flights SGN→DAD ngày 07/10", "check_seat chuyến sáng rẻ kế tiếp",
                                 "book_seat chuyến vừa kiểm", "pay booking vừa giữ",
                                 "get_booking để xác nhận"]))


def _trang_thai(nk: list) -> dict:
    s = dict(flights=None, checked={}, last_checked=None, code=None, paid=False, confirmed=None)
    for x in nk:
        t, a, kq = x["tool"], x["args"], x["ket_qua"]
        if t == "search_flights" and kq.get("status") == "ok":
            s["flights"] = kq["flights"]
        elif t == "check_seat":
            s["checked"][a.get("flight_id")] = kq
            s["last_checked"] = a.get("flight_id")
        elif t == "book_seat" and kq.get("status") == "ok":
            s["code"] = kq["booking_code"]
        elif t == "pay" and kq.get("status") == "ok":
            s["paid"] = True
        elif t == "get_booking" and kq.get("status") == "confirmed":
            s["confirmed"] = kq
    return s


def _ung_vien(s: dict) -> list:
    sang = [f for f in s["flights"] or [] if f["depart_time"] < YEU_CAU["truoc_gio"]]
    return [f["flight_id"] for f in sorted(sang, key=lambda f: f["gia_tham_khao"])]


def _hanh_dong(s: dict):
    """Chính sách ReAct: (tool, args) kế tiếp, hoặc None nếu đã xong / hết cách."""
    if s["flights"] is None:
        return "search_flights", {"origin": YEU_CAU["tu"], "destination": YEU_CAU["den"], "date": YEU_CAU["ngay"]}
    if s["confirmed"]:
        return None
    if s["paid"]:
        return "get_booking", {"booking_code": s["code"]}
    if s["code"]:
        return "pay", {"booking_code": s["code"]}
    for fid in _ung_vien(s):
        kq = s["checked"].get(fid)
        if kq is None or kq.get("status") == "error":
            return "check_seat", {"flight_id": fid}
        if kq["status"] == "ok" and kq["seats_left"] > 0 and kq["price"] <= YEU_CAU["tran_gia"]:
            return "book_seat", {"flight_id": fid}
    return None


def _args_cho_buoc(ten: str, s: dict) -> dict:
    """Vai thực thi: làm đúng tool của bước, suy tham số từ những gì đã có."""
    if ten == "search_flights":
        return _hanh_dong(dict(s, flights=None))[1]
    if ten == "check_seat":
        chua = [f for f in _ung_vien(s) if s["checked"].get(f, {}).get("status") in (None, "error")]
        return {"flight_id": (chua or [s["last_checked"] or ""])[0]}
    if ten == "book_seat":
        return {"flight_id": s["last_checked"] or ""}
    return {"booking_code": s["code"] or ""}


class ModelGia(BaseChatModel):
    @property
    def _llm_type(self) -> str:
        return "btvn3-model-gia"

    def bind_tools(self, tools: Any, **kwargs: Any) -> "ModelGia":
        return self

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **kwargs) -> ChatResult:
        return ChatResult(generations=[ChatGeneration(message=self._quyet_dinh(messages))])

    def _quyet_dinh(self, messages: list[BaseMessage]) -> AIMessage:
        i_cuoi = max(i for i, m in enumerate(messages) if m.type == "human")
        cuoi = str(messages[i_cuoi].content)

        if cuoi.startswith(LAP_KE_HOACH):
            return AIMessage(content=json.dumps({"ke_hoach": KE_HOACH_CO_DINH}, ensure_ascii=False))

        if cuoi.startswith(LAP_LAI):
            nk = [json.loads(d) for d in cuoi.splitlines() if d.startswith('{"tool"')]
            hd = _hanh_dong(_trang_thai(nk))
            con_lai = TEN_TOOL[TEN_TOOL.index(hd[0]):] if hd else []
            return AIMessage(content=json.dumps({"ke_hoach": [MO_TA_BUOC[t] for t in con_lai]},
                                                ensure_ascii=False))

        s = _trang_thai(nhat_ky(messages))
        if cuoi.startswith(BUOC):
            vua_lam = nhat_ky(messages[i_cuoi:])
            if vua_lam:
                return AIMessage(content=f"Xong bước {vua_lam[-1]['tool']}: "
                                         + json.dumps(vua_lam[-1]["ket_qua"], ensure_ascii=False))
            ten = min((t for t in TEN_TOOL if t in cuoi), key=cuoi.index)
            return self._goi(ten, _args_cho_buoc(ten, s), len(messages))

        hd = _hanh_dong(s)
        if hd:
            return self._goi(*hd, len(messages))
        if s["confirmed"]:
            b = s["confirmed"]
            return AIMessage(content=f"Đã đặt {b['booking_code']}: chuyến {b['flight_id']} "
                                     f"{b['depart_time']} ngày {b['depart_date']}, {vnd(b['price'])}.")
        return AIMessage(content="Không tìm được chuyến nào thoả mọi ràng buộc.")

    @staticmethod
    def _goi(ten: str, args: dict, n: int) -> AIMessage:
        return AIMessage(content="", tool_calls=[{"name": ten, "args": args, "id": f"call_{n}", "type": "tool_call"}])
