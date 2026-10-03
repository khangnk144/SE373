# -*- coding: utf-8 -*-
"""BTVN3 · Chạy một mẫu agent trên một kịch bản, đo chi phí, in kết quả. Dùng chung cho ba mẫu."""
import argparse
import time

from lib.harness import Harness, chot, in_ban_giao
from lib.tools_dat_ve import KICH_BAN, HangKhong


def tao_model(that: str | None):
    if that:
        from lib.model_that import model_that
        return model_that(that)
    from lib.model_gia import ModelGia
    return ModelGia()


def chay_mot(ten_mau: str, ham_chay, kich_ban: str, model, **kw) -> dict:
    """ham_chay(model, h, **kw) -> câu trả lời cuối. Mỗi lần chạy có thế giới và harness riêng."""
    h = Harness(HangKhong(kich_ban))
    t0 = time.perf_counter()
    tra_loi = ""
    try:
        tra_loi = ham_chay(model, h, **kw) or ""
    except Exception as e:      # lỗi mạng, lỗi định dạng của model thật: ghi thành kết cục, không nuốt
        h.dung("LỖI", f"{type(e).__name__}: {str(e)[:200]}", "Kiểm tra kết nối hoặc model rồi chạy lại?")
    bg = chot(h)
    return {"mau": ten_mau, "kich_ban": kich_ban, "ket_cuc": "ĐẠT" if bg is None else bg["loai"],
            "tra_loi": str(tra_loi), "ban_giao": bg, "da_thu": h.da_thu,
            "so_goi_model": h.so_goi_model, "so_goi_tool": h.so_goi_tool, "token": h.token,
            "giay": round(time.perf_counter() - t0, 1), "tac_dung_phu": h.hk.tac_dung_phu()}


def in_ket_qua(kq: dict) -> None:
    print("=" * 78)
    print(f"{kq['mau']} · kịch bản {kq['kich_ban']}")
    print("=" * 78)
    if kq["ban_giao"]:
        print(in_ban_giao(kq["ban_giao"]))
    else:
        for i, dong in enumerate(kq["da_thu"], 1):
            print(f"  {i}. {dong}")
        print(f"ĐẠT · {kq['tra_loi']}")
    print("-" * 78)
    print(f"Chi phí: {kq['so_goi_model']} lần gọi model · {kq['so_goi_tool']} lần gọi tool · "
          f"{kq['token']} token · {kq['giay']} giây")


def hoi_duyet(ke_hoach: list) -> bool:
    print("Kế hoạch cần duyệt:")
    for i, b in enumerate(ke_hoach, 1):
        print(f"  {i}. {b}")
    return input("Duyệt kế hoạch này? (y/n) ").strip().lower() == "y"


def cli(ten_mau: str, ham_chay, co_duyet: bool = False) -> None:
    p = argparse.ArgumentParser(description=f"BTVN3 · {ten_mau}")
    p.add_argument("--kich-ban", default="binh_thuong", choices=list(KICH_BAN))
    p.add_argument("--that", choices=["qwen", "gemma"], help="dùng model thật của UIT (cần mạng nội bộ)")
    if co_duyet:
        p.add_argument("--duyet", action="store_true", help="hỏi người duyệt kế hoạch trước khi chạy")
    a = p.parse_args()
    kw = {"duyet": hoi_duyet} if co_duyet and a.duyet else {}
    in_ket_qua(chay_mot(ten_mau, ham_chay, a.kich_ban, tao_model(a.that), **kw))
