---
name: csv-quality
description: Kiểm tra chất lượng file CSV danh sách công việc (cột task_id, owner, hours), tính tổng giờ theo người và xác định người quá tải theo ngưỡng giờ người dùng đưa ra, bằng script có sẵn, rồi ghi báo cáo Markdown dưới output/. Dùng khi người dùng yêu cầu kiểm tra, rà soát chất lượng dữ liệu CSV công việc, tính tổng giờ theo người hoặc tìm người vượt/quá tải giờ.
---

# CSV quality

Kiểm tra chất lượng CSV công việc và tính tổng giờ theo người bằng script, không tự đếm hay cộng bằng mắt.

## Ngưỡng giờ (bắt buộc)

- Script cần ngưỡng giờ `--max-hours`. Chỉ dùng con số người dùng nêu trong yêu cầu hiện tại (ví dụ người dùng hỏi "ai vượt N giờ" → `--max-hours N`), truyền đúng giá trị đó.
- Người dùng chưa nêu ngưỡng: hỏi lại ngưỡng rồi dừng. Không chạy script để kết luận, không tự chọn ngưỡng mặc định, không lấy ngưỡng từ cuộc trò chuyện hay lượt yêu cầu trước.

## Chạy script

Dùng tool `bash` (cwd là workspace). Lệnh đầy đủ:

```
python skills/csv-quality/scripts/check_csv.py --input <đường dẫn CSV> --max-hours <ngưỡng người dùng đưa ra>
```

Ví dụ với file `data/tasks.csv` và ngưỡng người dùng nêu là N giờ: `python skills/csv-quality/scripts/check_csv.py --input data/tasks.csv --max-hours N`

Không cần đọc source script để chạy. Chỉ đọc `scripts/check_csv.py` khi cần hiểu một hành vi mà phần dưới không mô tả.

## Kiểm tra kết quả

- `exit_code` 0: phân tích thành công. `stdout` là JSON gồm:
  - Chất lượng dữ liệu (tính trên toàn bộ dòng dữ liệu): `row_count`, `missing_owner_count`, `invalid_hours_count`, `duplicate_id_count`, `duplicate_ids`, `issues`.
  - Tổng giờ: `max_hours` (ngưỡng đã truyền), `hours_by_owner` (owner → tổng giờ, chỉ cộng dòng hợp lệ), `overloaded_owners` (danh sách `owner`, `total_hours` của người có tổng giờ **lớn hơn** ngưỡng; bằng ngưỡng không quá tải), `excluded_rows` (dòng không được cộng: `line`, `task_id`, `reasons`).
  - Mã lý do trong `reasons`: `wrong_field_count` (sai số trường), `missing_task_id` (thiếu task_id), `duplicate_id` (task_id đã xuất hiện ở dòng trước, chỉ giữ lần đầu), `missing_owner` (thiếu owner), `invalid_hours` (hours không phải số hữu hạn không âm).
  - Dữ liệu có lỗi, có dòng bị loại hoặc có người quá tải vẫn là exit 0.
- `exit_code` 1: **lỗi thực thi** (file không tồn tại, thiếu cột bắt buộc, lỗi parse). Đọc `stderr`, báo cho người dùng là không phân tích được. Không đưa tổng giờ, không bịa thống kê, không ghi báo cáo như thể đã phân tích.
- `exit_code` 2: thiếu hoặc sai `--max-hours`. Đọc `stderr`, hỏi lại người dùng ngưỡng hợp lệ (số không âm).
- `timed_out` true hoặc `ok` false: lệnh không chạy xong; báo lỗi, không suy đoán kết quả.
- Phân biệt rõ **lỗi dữ liệu** (nằm trong `issues`/`excluded_rows`, script vẫn chạy thành công) với **lỗi thực thi** (exit khác 0).

## Viết báo cáo

1. Đọc template `references/report-template.md` trong thư mục skill này, tức `skills/csv-quality/references/report-template.md`.
2. Lấy mọi con số từ JSON của script: ngưỡng từ `max_hours`, tổng giờ từ `hours_by_owner`, người vượt ngưỡng từ `overloaded_owners`, dòng bị loại từ `excluded_rows`. Không tự cộng lại hay suy ra con số khác.
3. Mỗi dòng bị loại ghi line number (header là line 1), task_id (trống ghi "(trống)") và tất cả lý do. Nêu rõ các dòng này không được cộng vào tổng giờ.
4. Không sửa file CSV khi người dùng chỉ yêu cầu kiểm tra. Có thể đề xuất cách sửa trong mục khuyến nghị.
5. Ghi báo cáo bằng `write_file` vào đường dẫn người dùng yêu cầu (mặc định `output/csv-quality.md`), rồi trả lời đường dẫn, ngưỡng, người vượt ngưỡng và tóm tắt ngắn.
