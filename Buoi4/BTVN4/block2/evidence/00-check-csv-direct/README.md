# Chạy trực tiếp check_csv.py

Thư mục chạy: `stage-04-script-skill`

| Trường hợp | Lệnh | Exit | Kết quả chính |
|---|---|---|---|
| CSV đề bài, ngưỡng 8 | `python workspace/skills/csv-quality/scripts/check_csv.py --input workspace/data/workload.csv --max-hours 8` | 0 | hours_by_owner={"Lan": 9, "Minh": 3}; overloaded=['Lan']; loại: dòng 5: invalid_hours, dòng 6: duplicate_id, dòng 7: missing_owner |
| CSV đề bài, ngưỡng 9 | `python workspace/skills/csv-quality/scripts/check_csv.py --input workspace/data/workload.csv --max-hours 9` | 0 | hours_by_owner={"Lan": 9, "Minh": 3}; overloaded=[]; loại: dòng 5: invalid_hours, dòng 6: duplicate_id, dòng 7: missing_owner |
| Trường hợp đặc biệt: ID đầu tiên có hours không hợp lệ, ngưỡng 0 | `python workspace/skills/csv-quality/scripts/check_csv.py --input workspace/data/workload-edge.csv --max-hours 0` | 0 | hours_by_owner={"Minh": 0}; overloaded=[]; loại: dòng 2: invalid_hours, dòng 3: duplicate_id |
| File không tồn tại | `python workspace/skills/csv-quality/scripts/check_csv.py --input workspace/data/khong-ton-tai.csv --max-hours 8` | 1 | stderr: ERROR: Không đọc được file workspace/data/khong-ton-tai.csv: No such file or directory |
| Thiếu --max-hours | `python workspace/skills/csv-quality/scripts/check_csv.py --input workspace/data/workload.csv` | 2 | stderr: check_csv.py: error: the following arguments are required: --max-hours |
| --max-hours không hợp lệ (-1) | `python workspace/skills/csv-quality/scripts/check_csv.py --input workspace/data/workload.csv --max-hours -1` | 2 | stderr: check_csv.py: error: argument --max-hours: '-1' không phải số hữu hạn không âm. |

CSV đầu vào không bị sửa sau khi chạy: có (workload-edge.csv, workload.csv)
