# Đánh giá ba mẫu · model: qwen · 3 lần/cặp

## Tổng hợp
| Mẫu | Đúng kỳ vọng | TB gọi model | TB gọi tool | TB token | TB giây | Lần trả tiền sai |
|---|---|---|---|---|---|---|
| ReAct | 9/15 | 5.6 | 7.6 | 9127.7 | 31.7 | 0 |
| Plan-then-Execute | 9/15 | 10.4 | 7.4 | 17504.0 | 38.7 | 0 |
| Lai | 6/15 | 10.0 | 6.8 | 15297.8 | 36.1 | 0 |

## Chi tiết
| Mẫu | Kịch bản | Kỳ vọng | Kết cục | Đúng | Gọi model | Gọi tool | Token | Giây | Tác dụng phụ |
|---|---|---|---|---|---|---|---|---|---|
| ReAct | binh_thuong | ĐẠT | ĐẠT | ✅ | 6 | 8 | 9575 | 26.6 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | binh_thuong | ĐẠT | ĐẠT | ✅ | 6 | 8 | 9575 | 26.3 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | binh_thuong | ĐẠT | ĐẠT | ✅ | 6 | 8 | 9575 | 26.3 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | het_cho | ĐẠT | ĐẠT | ✅ | 6 | 8 | 10230 | 36.1 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | het_cho | ĐẠT | ĐẠT | ✅ | 6 | 8 | 10230 | 35.7 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | het_cho | ĐẠT | ĐẠT | ✅ | 6 | 8 | 10230 | 35.7 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 3 | 5 | 4201 | 32.1 | — |
| ReAct | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 3 | 5 | 4252 | 34.5 | — |
| ReAct | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 3 | 5 | 4201 | 31.9 | — |
| ReAct | loi_timeout | LẶP | ĐẠT | ❌ | 7 | 9 | 11985 | 36.0 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | loi_timeout | LẶP | ĐẠT | ❌ | 7 | 9 | 12010 | 36.4 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | loi_timeout | LẶP | ĐẠT | ❌ | 7 | 9 | 11985 | 35.7 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | can_duyet | CẦN NGƯỜI DUYỆT | ĐẠT | ❌ | 6 | 8 | 9622 | 27.7 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | can_duyet | CẦN NGƯỜI DUYỆT | ĐẠT | ❌ | 6 | 8 | 9622 | 27.2 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | can_duyet | CẦN NGƯỜI DUYỆT | ĐẠT | ❌ | 6 | 8 | 9622 | 27.4 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | binh_thuong | ĐẠT | ĐẠT | ✅ | 11 | 8 | 18938 | 41.4 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | binh_thuong | ĐẠT | ĐẠT | ✅ | 11 | 8 | 18938 | 40.7 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | binh_thuong | ĐẠT | ĐẠT | ✅ | 11 | 8 | 18938 | 40.4 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | het_cho | ĐẠT | ĐẠT | ✅ | 11 | 8 | 18836 | 39.1 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | het_cho | ĐẠT | ĐẠT | ✅ | 11 | 8 | 18836 | 39.2 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | het_cho | ĐẠT | ĐẠT | ✅ | 11 | 8 | 18836 | 39.2 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 8 | 5 | 12148 | 34.9 | — |
| Plan-then-Execute | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 8 | 5 | 12148 | 34.8 | — |
| Plan-then-Execute | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 8 | 5 | 12148 | 34.8 | — |
| Plan-then-Execute | loi_timeout | LẶP | ĐẠT | ❌ | 11 | 8 | 18710 | 39.3 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | loi_timeout | LẶP | ĐẠT | ❌ | 11 | 8 | 18710 | 39.0 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | loi_timeout | LẶP | ĐẠT | ❌ | 11 | 8 | 18710 | 38.8 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | can_duyet | CẦN NGƯỜI DUYỆT | ĐẠT | ❌ | 11 | 8 | 18888 | 39.4 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | can_duyet | CẦN NGƯỜI DUYỆT | ĐẠT | ❌ | 11 | 8 | 18888 | 39.4 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | can_duyet | CẦN NGƯỜI DUYỆT | ĐẠT | ❌ | 11 | 8 | 18888 | 39.4 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Lai | binh_thuong | ĐẠT | ĐẠT | ✅ | 12 | 8 | 20058 | 41.3 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| Lai | binh_thuong | ĐẠT | ĐẠT | ✅ | 12 | 8 | 20058 | 41.1 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| Lai | binh_thuong | ĐẠT | ĐẠT | ✅ | 12 | 8 | 20058 | 41.2 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| Lai | het_cho | ĐẠT | CẦN NGƯỜI DUYỆT | ❌ | 7 | 5 | 8867 | 30.5 | — |
| Lai | het_cho | ĐẠT | CẦN NGƯỜI DUYỆT | ❌ | 7 | 5 | 8867 | 30.4 | — |
| Lai | het_cho | ĐẠT | CẦN NGƯỜI DUYỆT | ❌ | 7 | 5 | 8867 | 30.1 | — |
| Lai | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 6 | 5 | 6921 | 27.1 | — |
| Lai | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 6 | 5 | 6921 | 26.9 | — |
| Lai | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 6 | 5 | 6921 | 26.9 | — |
| Lai | loi_timeout | LẶP | ĐẠT | ❌ | 13 | 8 | 20636 | 42.0 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Lai | loi_timeout | LẶP | ĐẠT | ❌ | 13 | 8 | 20636 | 42.0 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Lai | loi_timeout | LẶP | ĐẠT | ❌ | 13 | 8 | 20636 | 41.5 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Lai | can_duyet | CẦN NGƯỜI DUYỆT | ĐẠT | ❌ | 12 | 8 | 20007 | 40.4 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Lai | can_duyet | CẦN NGƯỜI DUYỆT | ĐẠT | ❌ | 12 | 8 | 20007 | 39.9 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Lai | can_duyet | CẦN NGƯỜI DUYỆT | ĐẠT | ❌ | 12 | 8 | 20007 | 39.9 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
