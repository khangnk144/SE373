# -*- coding: utf-8 -*-
"""BTVN3 · Mẫu 2 · Plan-then-Execute.

Gọi model MỘT lần để sinh trọn kế hoạch → (người duyệt) → thực thi lần lượt từng
bước, mỗi bước do một sub-agent nhỏ làm. Kế hoạch KHÔNG đổi giữa chừng: đó là
điểm mạnh (duyệt trước, đoán trước chi phí) và cũng là điểm yếu (kế hoạch lỗi thời).

    python agent_plan_execute.py --kich-ban het_cho
    python agent_plan_execute.py --duyet            # tự tay duyệt kế hoạch
"""
from langchain_core.messages import HumanMessage

from lib.chay import cli
from lib.harness import Harness
from lib.ke_hoach import lap_ke_hoach, thuc_thi_buoc
from lib.rang_buoc import mo_ta_yeu_cau


def chay(model, h: Harness, duyet=None) -> str:
    ke_hoach = lap_ke_hoach(model, h)
    if h.ket_thuc:
        return ""
    if duyet and not duyet(ke_hoach):
        h.dung("CẦN NGƯỜI DUYỆT", "người duyệt từ chối kế hoạch", "Sửa yêu cầu hay lập kế hoạch khác?")
        return ""
    lich_su = [HumanMessage(mo_ta_yeu_cau())]
    for buoc in ke_hoach:
        lich_su = thuc_thi_buoc(model, h, buoc, lich_su)
        if h.ket_thuc:
            return ""
    return lich_su[-1].content


if __name__ == "__main__":
    cli("Plan-then-Execute", chay, co_duyet=True)
