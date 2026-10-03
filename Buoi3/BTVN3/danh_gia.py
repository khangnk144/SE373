# -*- coding: utf-8 -*-
"""BTVN3 · Đánh giá ba mẫu thiết kế trên cùng năm kịch bản.

Thí nghiệm có đối chứng: cùng tool, cùng harness, cùng yêu cầu; chỉ đổi mẫu.
Mỗi kịch bản có một kết cục KỲ VỌNG; agent tốt là agent dừng đúng kiểu, với chi phí thấp.

    python danh_gia.py                    # model giả: chỉ kiểm dây nối, số liệu là kịch bản
    python danh_gia.py --that qwen --so-lan 3
Kết quả in ra màn hình và ghi vào ket_qua/danh_gia_<model>.md để dán vào báo cáo.
"""
import argparse
from pathlib import Path

import agent_lai
import agent_plan_execute
import agent_react
from lib.chay import chay_mot, tao_model
from lib.tools_dat_ve import KICH_BAN

MAU = {"ReAct": agent_react.chay, "Plan-then-Execute": agent_plan_execute.chay, "Lai": agent_lai.chay}
KY_VONG = {
    "binh_thuong": "ĐẠT",
    "het_cho": "ĐẠT",
    "vuot_gia": "KHÔNG ĐẠT TIÊU CHÍ",
    "loi_timeout": "LẶP",
    "can_duyet": "CẦN NGƯỜI DUYỆT",
}


def bang_chi_tiet(ds: list) -> list:
    dong = ["| Mẫu | Kịch bản | Kỳ vọng | Kết cục | Đúng | Gọi model | Gọi tool | Token | Giây | Tác dụng phụ |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for k in ds:
        dong.append(f"| {k['mau']} | {k['kich_ban']} | {KY_VONG[k['kich_ban']]} | {k['ket_cuc']} | "
                    f"{'✅' if k['dung'] else '❌'} | {k['so_goi_model']} | {k['so_goi_tool']} | {k['token']} | "
                    f"{k['giay']} | {'; '.join(k['tac_dung_phu']) or '—'} |")
    return dong


def bang_tong_hop(ds: list) -> list:
    dong = ["| Mẫu | Đúng kỳ vọng | TB gọi model | TB gọi tool | TB token | TB giây | Lần trả tiền sai |",
            "|---|---|---|---|---|---|---|"]
    for ten in MAU:
        x = [k for k in ds if k["mau"] == ten]
        tb = lambda f: round(sum(k[f] for k in x) / len(x), 1)          # noqa: E731
        tra_sai = sum(1 for k in x if k["ket_cuc"] != "ĐẠT" and any("ĐÃ TRẢ TIỀN" in t for t in k["tac_dung_phu"]))
        dong.append(f"| {ten} | {sum(k['dung'] for k in x)}/{len(x)} | {tb('so_goi_model')} | "
                    f"{tb('so_goi_tool')} | {tb('token')} | {tb('giay')} | {tra_sai} |")
    return dong


def main() -> None:
    p = argparse.ArgumentParser(description="BTVN3 · đánh giá ba mẫu agent")
    p.add_argument("--that", choices=["qwen", "gemma"], help="dùng model thật của UIT (cần mạng nội bộ)")
    p.add_argument("--so-lan", type=int, default=1, help="số lần lặp mỗi cặp (model thật không tất định)")
    a = p.parse_args()

    ds = []
    for ten, ham in MAU.items():
        for kb in KICH_BAN:
            for lan in range(a.so_lan):
                kq = chay_mot(ten, ham, kb, tao_model(a.that))
                kq["dung"] = kq["ket_cuc"] == KY_VONG[kb]
                ds.append(kq)
                print(f"  {ten:<18} {kb:<12} lần {lan + 1}: {kq['ket_cuc']}", flush=True)

    ten_model = a.that or "model_gia"
    md = [f"# Đánh giá ba mẫu · model: {ten_model} · {a.so_lan} lần/cặp", "",
          "## Tổng hợp", *bang_tong_hop(ds), "", "## Chi tiết", *bang_chi_tiet(ds)]
    if not a.that:
        md[1:1] = ["", "> Model giả là chính sách viết tay: bảng này chỉ chứng minh harness và dây nối "
                   "chạy đúng, KHÔNG phải bằng chứng về hiệu quả của từng mẫu."]
    print("\n" + "\n".join(md))
    ra = Path(__file__).parent / "ket_qua" / f"danh_gia_{ten_model}.md"
    ra.parent.mkdir(exist_ok=True)
    ra.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nĐã ghi {ra}")


if __name__ == "__main__":
    main()
