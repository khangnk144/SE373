# -*- coding: utf-8 -*-
"""BTVN3 · Tool mockup đặt vé máy bay.

Dữ liệu tĩnh, không gọi mạng. Mỗi kịch bản chỉ ghi phần khác với mặc định, để
ba mẫu agent chạy trên cùng một "thế giới" và so sánh được với nhau.

    search_flights(origin, destination, date) -> danh sách chuyến + giá tham khảo
    check_seat(flight_id)                     -> số ghế, giá thật, hoàn được không
    book_seat(flight_id)                      -> giữ chỗ, trả mã đặt chỗ   (tác dụng phụ)
    pay(booking_code)                         -> thanh toán               (tác dụng phụ)
    get_booking(booking_code)                 -> đọc lại trạng thái đặt chỗ

Quy tắc observation: luôn có "status"; lỗi thì có mã lỗi, gợi ý và giá trị hợp lệ.
"""
from lib.rang_buoc import vnd

CHUYEN_BAY = [
    dict(flight_id="VJ604", airline="Vietjet", depart_time="06:15", gia_tham_khao=1_300_000),
    dict(flight_id="QH118", airline="Bamboo", depart_time="09:40", gia_tham_khao=1_400_000),
    dict(flight_id="VJ612", airline="Vietjet", depart_time="11:05", gia_tham_khao=1_600_000),
    dict(flight_id="VN122", airline="Vietnam Airlines", depart_time="07:30", gia_tham_khao=1_850_000),
    dict(flight_id="VN134", airline="Vietnam Airlines", depart_time="14:20", gia_tham_khao=1_200_000),
]
for _c in CHUYEN_BAY:
    _c.update({"from": "SGN", "to": "DAD", "depart_date": "07/10"})

# Kịch bản ↔ năm kiểu kết thúc trên slide (A, C, B, E) + một kịch bản làm kế hoạch lỗi thời.
KICH_BAN = {
    "binh_thuong": {},                                           # A · đặt được ngay
    "het_cho": {"VJ604": {"seats": 0}},                          # kế hoạch lập trước bị lỗi thời
    "vuot_gia": {"VJ604": {"price": 2_310_000}, "QH118": {"price": 2_450_000},
                 "VJ612": {"price": 2_190_000}, "VN122": {"price": 2_080_000}},   # B
    "loi_timeout": {"VJ604": {"error": "timeout"}},              # C · tool lỗi lặp lại
    "can_duyet": {"VJ604": {"price": 1_950_000, "refundable": False}},  # E · cần người duyệt
}


class HangKhong:
    """Một "thế giới" đặt vé cho một lần chạy. Ghi lại mọi tác dụng phụ."""

    def __init__(self, kich_ban: str = "binh_thuong"):
        self.kich_ban = kich_ban
        self.ghe = {c["flight_id"]: dict(price=c["gia_tham_khao"], seats=5, refundable=True)
                    for c in CHUYEN_BAY}
        for fid, doi in KICH_BAN[kich_ban].items():
            self.ghe[fid].update(doi)
        self.bookings = {}          # mã → booking
        self.gia_da_bao = {}        # flight_id → giá check_seat đã trả cho agent
        self.da_tim = False

    # ----------------------------------------------------------- tra cứu nội bộ
    def chuyen(self, flight_id: str) -> dict | None:
        return next((c for c in CHUYEN_BAY if c["flight_id"] == flight_id), None)

    def booking_moi_nhat(self) -> dict | None:
        return list(self.bookings.values())[-1] if self.bookings else None

    def tac_dung_phu(self) -> list:
        ra = []
        for b in self.bookings.values():
            ra.append(f"{b['booking_code']} giữ chỗ {b['flight_id']} ({vnd(b['price'])})")
            if b["paid"]:
                ra.append(f"{b['booking_code']} ĐÃ TRẢ TIỀN")
        return ra

    # ------------------------------------------------------------------- tools
    def search_flights(self, origin: str, destination: str, date: str) -> dict:
        """Tìm chuyến bay theo mã sân bay đi, đến (vd SGN, DAD) và ngày dạng dd/mm.
        Trả danh sách chuyến kèm giờ bay và giá THAM KHẢO; giá thật phải lấy bằng check_seat."""
        self.da_tim = True
        khop = [c for c in CHUYEN_BAY
                if (c["from"], c["to"], c["depart_date"]) == (origin.upper(), destination.upper(), date)]
        if not khop:
            return {"status": "ok", "count": 0, "flights": [],
                    "hint": "Dữ liệu chỉ có chặng SGN→DAD ngày 07/10"}
        return {"status": "ok", "count": len(khop),
                "flights": [{k: c[k] for k in ("flight_id", "airline", "depart_date",
                                              "depart_time", "gia_tham_khao")} for c in khop]}

    def check_seat(self, flight_id: str) -> dict:
        """Kiểm tra ghế trống, giá thật và điều kiện hoàn vé của một chuyến (flight_id lấy từ search_flights)."""
        if flight_id not in self.ghe:
            return {"status": "invalid_param", "param": "flight_id", "allowed": list(self.ghe)}
        g = self.ghe[flight_id]
        if "error" in g:
            return {"status": "error", "error": g["error"], "flight_id": flight_id, "retryable": True}
        self.gia_da_bao[flight_id] = g["price"]
        return {"status": "ok", "flight_id": flight_id, "seats_left": g["seats"],
                "price": g["price"], "refundable": g["refundable"]}

    def book_seat(self, flight_id: str) -> dict:
        """Giữ một ghế trên chuyến flight_id. Trả booking_code ở trạng thái held (chưa thanh toán)."""
        if flight_id not in self.ghe:
            return {"status": "invalid_param", "param": "flight_id", "allowed": list(self.ghe)}
        g = self.ghe[flight_id]
        if g["seats"] <= 0:
            return {"status": "error", "error": "sold_out", "flight_id": flight_id,
                    "hint": "Chọn chuyến khác bằng check_seat"}
        g["seats"] -= 1
        code = f"BK{100 + len(self.bookings)}"
        self.bookings[code] = {**self.chuyen(flight_id), "booking_code": code, "status": "held",
                               "paid": False, "price": g["price"], "refundable": g["refundable"]}
        self.bookings[code].pop("gia_tham_khao")
        return {"status": "ok", "booking_code": code, "booking_status": "held", "price": g["price"]}

    def pay(self, booking_code: str) -> dict:
        """Thanh toán booking đang held bằng thẻ công ty."""
        b = self.bookings.get(booking_code)
        if not b:
            return {"status": "invalid_param", "param": "booking_code", "allowed": list(self.bookings)}
        b["paid"], b["status"] = True, "confirmed"
        return {"status": "ok", "booking_code": booking_code, "paid": True, "amount": b["price"]}

    def get_booking(self, booking_code: str) -> dict:
        """Đọc lại trạng thái một booking: status, paid, chuyến, giờ, giá."""
        b = self.bookings.get(booking_code)
        if not b:
            return {"status": "invalid_param", "param": "booking_code", "allowed": list(self.bookings)}
        return dict(b)


TEN_TOOL = ["search_flights", "check_seat", "book_seat", "pay", "get_booking"]


def tools_langchain(hk: HangKhong) -> list:
    """Bọc các phương thức của hk thành tool LangChain cho create_agent."""
    from langchain_core.tools import tool
    return [tool(getattr(hk, ten)) for ten in TEN_TOOL]
