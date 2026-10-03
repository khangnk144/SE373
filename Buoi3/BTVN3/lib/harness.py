# -*- coding: utf-8 -*-
"""BTVN3 · Lớp harness cho agent đặt vé. Framework không làm hộ phần này.

Thứ tự kiểm theo checklist slide 35:
    0  trước khi thực thi tool   kiểm quyền (hành động có tác dụng phụ)      → CẦN NGƯỜI DUYỆT
       trước khi thực thi tool   kiểm ràng buộc (chặn, trả observation lỗi)  → agent tự đổi hướng
    1  khi agent tự cho là xong  tiêu chí hoàn thành, kiểm bằng code          → ĐẠT / KHÔNG ĐẠT
    2  sau mỗi observation       (tool, args) trùng                          → LẶP
    3  sau mỗi observation       đại lượng tiến triển đứng yên               → BẾ TẮC
    4  cuối cùng                 ngân sách số lần gọi model                  → HẾT NGÂN SÁCH
Mọi kiểu dừng bất thường đều trả gói bàn giao, không dừng im lặng.
"""
import json
from collections import deque

from langchain.agents.middleware import AgentMiddleware, hook_config
from langchain_core.messages import AIMessage, ToolMessage

from lib.rang_buoc import can_duyet, tieu_chi_hoan_thanh, vi_pham_rang_buoc, vnd

# Gọi lại get_booking để chờ trạng thái đổi là polling hợp lệ, không tính là lặp.
KHONG_KIEM_LAP = {"get_booking"}


class LoopDetector:
    """repeat_k=3: cho phép thử lại một lần khi tool timeout, lần thứ ba mới là lặp."""

    def __init__(self, window=6, repeat_k=3, stall_n=5):
        self.recent = deque(maxlen=window)
        self.k, self.n = repeat_k, stall_n
        self.last_progress, self.stall = None, 0

    def check(self, tool: str, args: dict, progress=None):
        fp = (tool, repr(sorted(args.items())))
        if tool not in KHONG_KIEM_LAP and self.recent.count(fp) + 1 >= self.k:
            return f"LẶP · {tool}({args}) lần thứ {self.recent.count(fp) + 1} trong {self.recent.maxlen} lời gọi gần nhất"
        self.recent.append(fp)
        self.stall = self.stall + 1 if progress == self.last_progress else 0
        self.last_progress = progress
        if self.stall >= self.n:
            return f"BẾ TẮC · tiến triển đứng yên ở {progress}/4 qua {self.stall} lời gọi"
        return None


class Harness:
    """Trạng thái harness của MỘT lần chạy, dùng chung cho mọi sub-agent trong lần chạy đó."""

    def __init__(self, hk, ngan_sach_model=20):
        self.hk, self.ngan_sach = hk, ngan_sach_model
        self.so_goi_model = self.so_goi_tool = self.token = 0
        self.lap = LoopDetector()
        self.da_thu = []
        self.ket_thuc = None            # gói bàn giao khi dừng bất thường

    # ------------------------------------------------------------ ghi nhận
    def ghi_goi_model(self, ai) -> None:
        self.so_goi_model += 1
        self.token += (getattr(ai, "usage_metadata", None) or {}).get("total_tokens", 0)

    def ghi_tool(self, call: dict, ket_qua) -> None:
        self.so_goi_tool += 1
        tom_tat = ket_qua if isinstance(ket_qua, str) else json.dumps(ket_qua, ensure_ascii=False)
        self.da_thu.append(f"{call['name']}({call['args']}) → {tom_tat[:90]}")

    def tien_trien(self) -> int:
        """Đã tìm · đã thấy chuyến hợp lệ còn ghế · đã giữ chỗ · đã trả tiền (0–4)."""
        hk, b = self.hk, self.hk.booking_moi_nhat()
        hop_le = any(not vi_pham_rang_buoc(hk.chuyen(f), p) and hk.ghe[f]["seats"] > 0
                     for f, p in hk.gia_da_bao.items())
        return sum([hk.da_tim, hop_le, b is not None, bool(b and b["paid"])])

    def dung(self, loai: str, ly_do: str, cau_hoi: str) -> dict:
        self.ket_thuc = {
            "loai": loai,
            "stop_reason": ly_do,
            "da_thu": list(self.da_thu),
            "trang_thai": {"tien_trien": f"{self.tien_trien()}/4",
                           "tac_dung_phu": self.hk.tac_dung_phu() or ["chưa có"]},
            "cau_hoi_cho_nguoi": cau_hoi,
        }
        return self.ket_thuc

    # ------------------------------------------------------------ kiểm tra
    def gia_that(self, tool: str, args: dict):
        """(chuyến, giá, hoàn được) lấy từ hệ thống, không tin con số model tự nói."""
        if tool == "book_seat":
            fid = args.get("flight_id")
        elif tool == "pay":
            b = self.hk.bookings.get(args.get("booking_code"))
            fid = b and b["flight_id"]
        else:
            return None
        g = self.hk.ghe.get(fid)
        return (self.hk.chuyen(fid), g["price"], g["refundable"]) if g else None

    def kiem_truoc_tool(self, tool_calls: list) -> dict | None:
        for c in tool_calls:                                        # 0 · kiểm quyền
            tt = self.gia_that(c["name"], c["args"])
            if tt and not vi_pham_rang_buoc(tt[0], tt[1]):          # vi phạm thì wrap_tool_call chặn
                ly_do = can_duyet(tt[1], tt[2])
                if ly_do:
                    return self.dung("CẦN NGƯỜI DUYỆT",
                                     f"định gọi {c['name']}({c['args']}) · " + "; ".join(ly_do),
                                     f"Duyệt {c['name']} chuyến {tt[0]['flight_id']} {tt[0]['depart_time']} "
                                     f"giá {vnd(tt[1])}{'' if tt[2] else ', vé KHÔNG hoàn'}? (có/không)")
        for c in tool_calls:                                        # 2, 3 · lặp và bế tắc
            canh_bao = self.lap.check(c["name"], c["args"], progress=self.tien_trien())
            if canh_bao:
                loai = "LẶP" if canh_bao.startswith("LẶP") else "BẾ TẮC"
                return self.dung(loai, canh_bao,
                                 f"{c['name']} không cho kết quả mới. Thử lại sau, "
                                 "hay cho phép bỏ qua để xét phương án khác?")
        if tool_calls and self.so_goi_model >= self.ngan_sach:     # 4 · ngân sách, kiểm cuối
            return self.dung("HẾT NGÂN SÁCH", f"đã gọi model {self.so_goi_model}/{self.ngan_sach} lần",
                             "Tăng ngân sách để chạy tiếp, hay dừng với kết quả dở dang?")
        return None


def chot(h: Harness) -> dict | None:
    """1 · Tiêu chí hoàn thành: đọc lại booking qua get_booking rồi kiểm bằng code."""
    if h.ket_thuc:
        return h.ket_thuc
    b = h.hk.booking_moi_nhat()
    booking = h.hk.get_booking(b["booking_code"]) if b else None
    tc = tieu_chi_hoan_thanh(booking, h.hk.gia_da_bao.get(booking and booking.get("flight_id")))
    if tc["dat"]:
        return None
    return h.dung("KHÔNG ĐẠT TIÊU CHÍ", "agent dừng nhưng chưa đạt: " + "; ".join(tc["thieu"]),
                  "Chưa đặt được vé thoả mọi ràng buộc. Nới ràng buộc nào (giá, giờ, ngày), hay huỷ yêu cầu?")


def in_ban_giao(b: dict) -> str:
    return "\n".join([
        f"DỪNG · {b['loai']} · {b['stop_reason']}",
        "  Đã thử       : " + ("\n                 ".join(b["da_thu"]) or "chưa gọi tool nào"),
        f"  Trạng thái   : tiến triển {b['trang_thai']['tien_trien']} · tác dụng phụ: "
        + "; ".join(b["trang_thai"]["tac_dung_phu"]),
        f"  Hỏi người    : {b['cau_hoi_cho_nguoi']}",
    ])


class HarnessMiddleware(AgentMiddleware):
    """Cắm Harness vào vòng lặp của create_agent."""

    def __init__(self, h: Harness):
        super().__init__()
        self.h = h

    @hook_config(can_jump_to=["end"])
    def after_model(self, state, runtime):
        cuoi = state["messages"][-1]
        self.h.ghi_goi_model(cuoi)
        bg = self.h.kiem_truoc_tool(getattr(cuoi, "tool_calls", None) or [])
        if bg:
            return {"jump_to": "end", "messages": [AIMessage(content=in_ban_giao(bg))]}
        return None

    def wrap_tool_call(self, request, handler):
        c = request.tool_call
        tt = self.h.gia_that(c["name"], c["args"])
        vi_pham = vi_pham_rang_buoc(tt[0], tt[1]) if tt else []
        if vi_pham:                     # chặn bằng code, trả observation có hướng đi khác
            obs = {"status": "blocked", "error": "constraint_violation", "vi_pham": vi_pham,
                   "hint": "Chọn chuyến khác thoả ràng buộc"}
            self.h.ghi_tool(c, obs)
            return ToolMessage(content=json.dumps(obs, ensure_ascii=False),
                               tool_call_id=c["id"], name=c["name"])
        msg = handler(request)
        self.h.ghi_tool(c, msg.content)
        return msg
