# Đánh giá ba mẫu · model: model_gia · 1 lần/cặp

> Model giả là chính sách viết tay: bảng này chỉ chứng minh harness và dây nối chạy đúng, KHÔNG phải bằng chứng về hiệu quả của từng mẫu.

## Tổng hợp
| Mẫu | Đúng kỳ vọng | TB gọi model | TB gọi tool | TB token | TB giây | Lần trả tiền sai |
|---|---|---|---|---|---|---|
| ReAct | 5/5 | 5.2 | 4.2 | 0.0 | 0.0 | 0 |
| Plan-then-Execute | 3/5 | 10.0 | 4.4 | 0.0 | 0.1 | 1 |
| Lai | 5/5 | 11.6 | 4.2 | 0.0 | 0.1 | 0 |

## Chi tiết
| Mẫu | Kịch bản | Kỳ vọng | Kết cục | Đúng | Gọi model | Gọi tool | Token | Giây | Tác dụng phụ |
|---|---|---|---|---|---|---|---|---|---|
| ReAct | binh_thuong | ĐẠT | ĐẠT | ✅ | 6 | 5 | 0 | 0.0 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | het_cho | ĐẠT | ĐẠT | ✅ | 7 | 6 | 0 | 0.0 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 6 | 5 | 0 | 0.0 | — |
| ReAct | loi_timeout | LẶP | LẶP | ✅ | 4 | 3 | 0 | 0.0 | — |
| ReAct | can_duyet | CẦN NGƯỜI DUYỆT | CẦN NGƯỜI DUYỆT | ✅ | 3 | 2 | 0 | 0.0 | — |
| Plan-then-Execute | binh_thuong | ĐẠT | ĐẠT | ✅ | 11 | 5 | 0 | 0.1 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | het_cho | ĐẠT | KHÔNG ĐẠT TIÊU CHÍ | ❌ | 11 | 5 | 0 | 0.1 | — |
| Plan-then-Execute | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 11 | 5 | 0 | 0.1 | — |
| Plan-then-Execute | loi_timeout | LẶP | KHÔNG ĐẠT TIÊU CHÍ | ❌ | 11 | 5 | 0 | 0.1 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | can_duyet | CẦN NGƯỜI DUYỆT | CẦN NGƯỜI DUYỆT | ✅ | 6 | 2 | 0 | 0.1 | — |
| Lai | binh_thuong | ĐẠT | ĐẠT | ✅ | 12 | 5 | 0 | 0.1 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| Lai | het_cho | ĐẠT | ĐẠT | ✅ | 15 | 6 | 0 | 0.1 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Lai | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 15 | 5 | 0 | 0.1 | — |
| Lai | loi_timeout | LẶP | LẶP | ✅ | 10 | 3 | 0 | 0.1 | — |
| Lai | can_duyet | CẦN NGƯỜI DUYỆT | CẦN NGƯỜI DUYỆT | ✅ | 6 | 2 | 0 | 0.0 | — |
