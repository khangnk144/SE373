# Đánh giá ba mẫu · model: gemma · 3 lần/cặp

## Tổng hợp
| Mẫu | Đúng kỳ vọng | TB gọi model | TB gọi tool | TB token | TB giây | Lần trả tiền sai |
|---|---|---|---|---|---|---|
| ReAct | 12/15 | 5.8 | 4.8 | 5754.5 | 2.3 | 0 |
| Plan-then-Execute | 11/15 | 10.3 | 4.7 | 12067.9 | 5.0 | 0 |
| Lai | 12/15 | 11.6 | 5.1 | 13317.9 | 5.2 | 0 |

## Chi tiết
| Mẫu | Kịch bản | Kỳ vọng | Kết cục | Đúng | Gọi model | Gọi tool | Token | Giây | Tác dụng phụ |
|---|---|---|---|---|---|---|---|---|---|
| ReAct | binh_thuong | ĐẠT | ĐẠT | ✅ | 6 | 5 | 5919 | 2.3 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | binh_thuong | ĐẠT | ĐẠT | ✅ | 6 | 5 | 5919 | 2.3 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | binh_thuong | ĐẠT | ĐẠT | ✅ | 6 | 5 | 5919 | 2.0 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | het_cho | ĐẠT | ĐẠT | ✅ | 7 | 6 | 7197 | 2.8 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | het_cho | ĐẠT | ĐẠT | ✅ | 7 | 6 | 7197 | 2.4 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | het_cho | ĐẠT | ĐẠT | ✅ | 7 | 6 | 7201 | 2.3 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 6 | 5 | 6041 | 3.3 | — |
| ReAct | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 6 | 5 | 6041 | 3.2 | — |
| ReAct | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 6 | 5 | 6041 | 3.3 | — |
| ReAct | loi_timeout | LẶP | ĐẠT | ❌ | 7 | 6 | 7139 | 2.7 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | loi_timeout | LẶP | ĐẠT | ❌ | 7 | 6 | 7139 | 2.5 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | loi_timeout | LẶP | ĐẠT | ❌ | 7 | 6 | 7139 | 2.3 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| ReAct | can_duyet | CẦN NGƯỜI DUYỆT | CẦN NGƯỜI DUYỆT | ✅ | 3 | 2 | 2475 | 0.9 | — |
| ReAct | can_duyet | CẦN NGƯỜI DUYỆT | CẦN NGƯỜI DUYỆT | ✅ | 3 | 2 | 2475 | 1.0 | — |
| ReAct | can_duyet | CẦN NGƯỜI DUYỆT | CẦN NGƯỜI DUYỆT | ✅ | 3 | 2 | 2475 | 1.0 | — |
| Plan-then-Execute | binh_thuong | ĐẠT | ĐẠT | ✅ | 11 | 5 | 12553 | 4.9 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | binh_thuong | ĐẠT | ĐẠT | ✅ | 11 | 5 | 13009 | 5.4 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | binh_thuong | ĐẠT | ĐẠT | ✅ | 11 | 5 | 12902 | 5.0 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | het_cho | ĐẠT | ĐẠT | ✅ | 12 | 6 | 14298 | 5.4 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | het_cho | ĐẠT | ĐẠT | ✅ | 14 | 8 | 18375 | 6.3 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | het_cho | ĐẠT | KHÔNG ĐẠT TIÊU CHÍ | ❌ | 9 | 3 | 9856 | 4.4 | — |
| Plan-then-Execute | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 11 | 5 | 13407 | 6.1 | — |
| Plan-then-Execute | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 11 | 5 | 12623 | 4.8 | — |
| Plan-then-Execute | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 11 | 5 | 13360 | 6.0 | — |
| Plan-then-Execute | loi_timeout | LẶP | ĐẠT | ❌ | 12 | 6 | 14497 | 5.4 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | loi_timeout | LẶP | ĐẠT | ❌ | 12 | 6 | 14542 | 5.4 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | loi_timeout | LẶP | ĐẠT | ❌ | 12 | 6 | 14537 | 5.9 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Plan-then-Execute | can_duyet | CẦN NGƯỜI DUYỆT | CẦN NGƯỜI DUYỆT | ✅ | 6 | 2 | 5685 | 3.5 | — |
| Plan-then-Execute | can_duyet | CẦN NGƯỜI DUYỆT | CẦN NGƯỜI DUYỆT | ✅ | 6 | 2 | 5686 | 3.3 | — |
| Plan-then-Execute | can_duyet | CẦN NGƯỜI DUYỆT | CẦN NGƯỜI DUYỆT | ✅ | 6 | 2 | 5689 | 3.3 | — |
| Lai | binh_thuong | ĐẠT | ĐẠT | ✅ | 12 | 5 | 13963 | 5.4 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| Lai | binh_thuong | ĐẠT | ĐẠT | ✅ | 12 | 5 | 13974 | 5.4 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| Lai | binh_thuong | ĐẠT | ĐẠT | ✅ | 12 | 5 | 13981 | 5.3 | BK100 giữ chỗ VJ604 (1.300.000đ); BK100 ĐÃ TRẢ TIỀN |
| Lai | het_cho | ĐẠT | ĐẠT | ✅ | 16 | 7 | 20191 | 7.1 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Lai | het_cho | ĐẠT | ĐẠT | ✅ | 16 | 7 | 19307 | 6.3 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Lai | het_cho | ĐẠT | ĐẠT | ✅ | 16 | 7 | 19334 | 6.4 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Lai | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 9 | 5 | 9352 | 4.5 | — |
| Lai | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 9 | 5 | 9089 | 3.7 | — |
| Lai | vuot_gia | KHÔNG ĐẠT TIÊU CHÍ | KHÔNG ĐẠT TIÊU CHÍ | ✅ | 9 | 5 | 9383 | 4.3 | — |
| Lai | loi_timeout | LẶP | ĐẠT | ❌ | 16 | 7 | 19915 | 6.8 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Lai | loi_timeout | LẶP | ĐẠT | ❌ | 14 | 6 | 16061 | 5.7 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Lai | loi_timeout | LẶP | ĐẠT | ❌ | 15 | 7 | 18225 | 7.4 | BK100 giữ chỗ QH118 (1.400.000đ); BK100 ĐÃ TRẢ TIỀN |
| Lai | can_duyet | CẦN NGƯỜI DUYỆT | CẦN NGƯỜI DUYỆT | ✅ | 6 | 2 | 5685 | 3.4 | — |
| Lai | can_duyet | CẦN NGƯỜI DUYỆT | CẦN NGƯỜI DUYỆT | ✅ | 6 | 2 | 5682 | 3.5 | — |
| Lai | can_duyet | CẦN NGƯỜI DUYỆT | CẦN NGƯỜI DUYỆT | ✅ | 6 | 2 | 5627 | 3.2 | — |
