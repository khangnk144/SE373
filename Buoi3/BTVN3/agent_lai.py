# -*- coding: utf-8 -*-
"""BTVN3 · Mẫu 3 · Lai (ReAct + Plan), theo slide 24.

Lập kế hoạch → thực thi từng bước → nếu observation lệch đáng kể thì lập lại kế
hoạch cho phần còn lại, không thì làm tiếp. "Lệch đáng kể" do CODE quyết định
(ke_hoach_lech), nên chỉ tốn thêm lời gọi model khi thật sự cần lập lại.

    python agent_lai.py --kich-ban het_cho
"""
from langchain_core.messages import HumanMessage

from lib.chay import cli
from lib.harness import Harness
from lib.ke_hoach import ke_hoach_lech, lap_ke_hoach, lap_lai_ke_hoach, nhat_ky, thuc_thi_buoc
from lib.rang_buoc import mo_ta_yeu_cau

LAP_LAI_TOI_DA = 5


def chay(model, h: Harness) -> str:
    ke_hoach = lap_ke_hoach(model, h)
    lich_su = [HumanMessage(mo_ta_yeu_cau())]
    so_lan_lap_lai = 0
    while ke_hoach and not h.ket_thuc:
        truoc = len(nhat_ky(lich_su))
        lich_su = thuc_thi_buoc(model, h, ke_hoach.pop(0), lich_su)
        if h.ket_thuc:
            break
        if ke_hoach_lech(nhat_ky(lich_su)[truoc:]):
            if so_lan_lap_lai >= LAP_LAI_TOI_DA:
                h.dung("HẾT NGÂN SÁCH", f"đã lập lại kế hoạch {so_lan_lap_lai} lần",
                       "Tăng số lần lập lại, hay dừng với kết quả dở dang?")
                break
            ke_hoach = lap_lai_ke_hoach(model, h, lich_su)
            so_lan_lap_lai += 1
    return "" if h.ket_thuc else lich_su[-1].content


if __name__ == "__main__":
    cli("Lai", chay)
