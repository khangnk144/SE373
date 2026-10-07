# Báo cáo chất lượng dữ liệu và tổng giờ: `{đường dẫn CSV}`

Công cụ: `skills/csv-quality/scripts/check_csv.py` | exit code: {exit_code} | ngưỡng: {max_hours} giờ

## Tổng giờ theo người
Chỉ cộng dòng hợp lệ; các dòng ở mục "Dòng bị loại" không được cộng. Quá tải khi tổng giờ lớn hơn ngưỡng {max_hours} giờ (bằng ngưỡng không quá tải).

| Owner | Tổng giờ | Vượt ngưỡng? |
|---|---|---|
| {owner} | {hours_by_owner[owner]} | {Có nếu owner nằm trong overloaded_owners, ngược lại Không} |

## Người vượt ngưỡng
- {owner}: {total_hours} giờ (> {max_hours} giờ)
- Nếu `overloaded_owners` rỗng: "Không ai vượt ngưỡng {max_hours} giờ."

## Dòng bị loại
| Line | task_id | Lý do |
|---|---|---|
| {line} | {task_id hoặc (trống)} | {mọi mã trong reasons, kèm giải thích ngắn} |

## Tổng quan chất lượng dữ liệu
| Chỉ số | Giá trị |
|---|---|
| Số dòng dữ liệu (không tính header) | {row_count} |
| Dòng thiếu owner | {missing_owner_count} |
| Dòng hours không hợp lệ | {invalid_hours_count} |
| Số task_id bị lặp (distinct) | {duplicate_id_count} ({duplicate_ids}) |

## Chi tiết lỗi
| Line | Cột | Loại | task_id | Mô tả |
|---|---|---|---|---|
| {line} | {column} | {type} | {task_id} | {message} |

## Khuyến nghị
- {Cách sửa đề xuất cho từng nhóm lỗi; không tự sửa file nguồn}
