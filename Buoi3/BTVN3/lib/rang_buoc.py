# -*- coding: utf-8 -*-
"""BTVN3 · Ràng buộc là dữ liệu.

Yêu cầu người dùng và chính sách công ty nằm ở MỘT chỗ. Prompt, lớp kiểm
ràng buộc, lớp kiểm quyền và tiêu chí hoàn thành đều đọc từ đây, không ai
phải "nhớ lại" yêu cầu từ hội thoại.
"""

YEU_CAU = {
    "tu": "SGN",
    "den": "DAD",
    "ngay": "07/10",
    "truoc_gio": "12:00",          # bay buổi sáng
    "tran_gia": 2_000_000,
}

CHINH_SACH = {
    "han_muc_tu_duyet": 1_500_000,           # trên mức này phải có người duyệt
    "ve_khong_hoan_can_duyet": True,
    "hanh_dong_tac_dung_phu": ["book_seat", "pay"],
}


def vnd(so: int) -> str:
    return f"{so:,}đ".replace(",", ".")


def mo_ta_yeu_cau(yc: dict = YEU_CAU) -> str:
    return (f"Đặt 1 vé {yc['tu']} → {yc['den']} ngày {yc['ngay']}, khởi hành trước "
            f"{yc['truoc_gio']}, giá không quá {vnd(yc['tran_gia'])}.")


def prompt_he_thong(yc: dict = YEU_CAU) -> str:
    """Prompt sinh ra từ dữ liệu, nên sửa YEU_CAU là prompt đổi theo."""
    return (
        "Bạn là trợ lý đặt vé máy bay.\n"
        f"Ràng buộc cứng: {mo_ta_yeu_cau(yc)}\n"
        "Quy trình: search_flights → check_seat (lấy giá thật) → book_seat → pay → get_booking.\n"
        "Chỉ dùng dữ liệu tool trả về, không tự đoán mã chuyến hay giá. "
        "Khi get_booking trả status confirmed thì trả lời mã đặt chỗ, chuyến, giờ, giá rồi dừng."
    )


def vi_pham_rang_buoc(chuyen: dict, gia: int, yc: dict = YEU_CAU) -> list:
    """Chuyến + giá thật có phạm ràng buộc nào không. Trả danh sách vi phạm."""
    loi = []
    if chuyen["depart_date"] != yc["ngay"]:
        loi.append(f"ngày {chuyen['depart_date']} ≠ {yc['ngay']}")
    if chuyen["depart_time"] >= yc["truoc_gio"]:
        loi.append(f"giờ {chuyen['depart_time']} không trước {yc['truoc_gio']}")
    if gia > yc["tran_gia"]:
        loi.append(f"giá {vnd(gia)} > trần {vnd(yc['tran_gia'])}")
    return loi


def can_duyet(gia: int, hoan_duoc: bool, cs: dict = CHINH_SACH) -> list:
    """Lý do hành động có tác dụng phụ cần người duyệt. Rỗng nghĩa là được tự làm."""
    ly_do = []
    if gia > cs["han_muc_tu_duyet"]:
        ly_do.append(f"giá {vnd(gia)} vượt hạn mức tự duyệt {vnd(cs['han_muc_tu_duyet'])}")
    if not hoan_duoc and cs["ve_khong_hoan_can_duyet"]:
        ly_do.append("vé không hoàn được")
    return ly_do


def tieu_chi_hoan_thanh(booking: dict | None, gia_da_thay: int | None,
                        yc: dict = YEU_CAU) -> dict:
    """Kiểm bằng code, không tin lời model tự tuyên bố xong.

    booking phải được đọc lại qua get_booking (kiểm chứng chéo), gia_da_thay là
    giá check_seat đã báo cho agent: hai con số phải khớp.
    """
    if not booking or booking.get("status") not in ("held", "confirmed"):
        return {"dat": False, "thieu": ["chưa có booking nào"]}
    kiem = {
        "status == confirmed": booking["status"] == "confirmed",
        "đã thanh toán": booking["paid"] is True,
        f"đúng chặng {yc['tu']}→{yc['den']}": (booking["from"], booking["to"]) == (yc["tu"], yc["den"]),
        f"ngày == {yc['ngay']}": booking["depart_date"] == yc["ngay"],
        f"giờ < {yc['truoc_gio']}": booking["depart_time"] < yc["truoc_gio"],
        f"giá ≤ {vnd(yc['tran_gia'])}": booking["price"] <= yc["tran_gia"],
        "giá khớp giá check_seat đã báo": gia_da_thay == booking["price"],
    }
    thieu = [ten for ten, dat in kiem.items() if not dat]
    return {"dat": not thieu, "thieu": thieu}
