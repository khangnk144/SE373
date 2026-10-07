# Báo cáo chất lượng dữ liệu và tổng giờ: `data/workload.csv`

Công cụ: `skills/csv-quality/scripts/check_csv.py` | exit code: 0 | ngưỡng: 9 giờ

## Tổng giờ theo người
Chỉ cộng dòng hợp lệ; các dòng ở mục "Dòng bị loại" không được cộng. Quá tải khi tổng giờ lớn hơn ngưỡng 9 giờ (bằng ngưỡng không quá tải).

| Owner | Tổng giờ | Vượt ngưỡng? |
|---|---|---|
| Lan | 9 | Không |
| Minh | 3 | Không |

## Người vượt ngưỡng
- Không ai vượt ngưỡng 9 giờ.

## Dòng bị loại
| Line | task_id | Lý do |
|---|---|---|
| 5 | T04 | invalid_hours (hours không phải số hữu hạn không âm) |
| 6 | T02 | duplicate_id (task_id đã xuất hiện ở dòng trước, chỉ giữ lần đầu) |
| 7 | T05 | missing_owner (thiếu owner) |

## Tổng quan chất lượng dữ liệu
| Chỉ số | Giá trị |
|---|---|
| Số dòng dữ liệu (không tính header) | 6 |
| Dòng thiếu owner | 1 |
| Dòng hours không hợp lệ | 1 |
| Số task_id bị lặp (distinct) | 1 (T02) |

## Chi tiết lỗi
| Line | Cột | Loại | task_id | Mô tả |
|---|---|---|---|---|
| 5 | hours | invalid_hours | T04 | hours 'abc' không phải số hữu hạn không âm. |
| 6 | task_id | duplicate_id | T02 | task_id T02 đã xuất hiện ở line 3. |
| 7 | owner | missing_owner | T05 | owner trống. |

## Khuyến nghị
- Dòng 5 (T04): thay `hours` bằng một số không âm hợp lệ.
- Dòng 6 (T02): đổi task_id thành giá trị duy nhất khác, hoặc bỏ dòng nếu trùng lặp.
- Dòng 7 (T05): điền owner cho task T05.
