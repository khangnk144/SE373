# Block 2: Kiểm tra quá tải theo người (Stage 03 → 04)

## 1. Môi trường chạy

| Mục | Giá trị |
|---|---|
| Model (bằng chứng nộp) | **Qwen3.8-27B** (`qwen3.8-27b`) của `llm.uit.edu.vn`, tắt chế độ suy nghĩ. Đi qua SSH SOCKS tunnel tới `192.168.20.150` và proxy `../uit-tool-call-proxy.py` (giải thích ở `../block1/analysis.md`, mục 1). Model tự quyết định tool call; proxy chỉ parse text `<tool_call>` thành `tool_calls` chuẩn |
| Máy | Windows 11, Python 3.13 trong `.venv` dùng chung của `agent-tools-skills-lab` |
| Cách chạy agent | `../run-scenario.py`: chạy đúng `app.py` của stage qua Streamlit `AppTest` (cách test của lab). Mỗi kịch bản là một lần tải trang + cuộc trò chuyện mới. Trace JSONL do chính app ghi vào `<stage>/traces/` |
| Bằng chứng mỗi kịch bản | `evidence/<kịch bản>/`: `transcript.md` (đọc nhanh), `conversation.json` (Conversation JSON của app), `traces/*.jsonl` (bản sao trace của app), `api-calls.jsonl` (mọi request/response HTTP, có text gốc của model, không có header/API key), `output/` (file báo cáo agent ghi) |
| Lần chạy đối chiếu | Toàn bộ kịch bản cũng đã chạy với `ministral-3b-2512` (Mistral) và đều đạt. Bằng chứng nằm trong `evidence/_mistral-ministral-3b/`, xem mục 7 |

**Thay đổi môi trường, không thuộc bài làm:** `tools/bash.py` của stage 03 và 04 gọi `bash -c`. Trên Windows, lệnh `bash` trỏ tới launcher WSL trong System32, mà máy không có distro Linux nên lệnh hỏng. Trước khi vá, stage 03 có 9 test fail: 7 do bash, 2 do symlink. Đã vá tối thiểu, chỉ có tác dụng khi `os.name == "nt"`:
- Dùng `bash.exe` của Git for Windows.
- PATH dạng Windows để Git Bash tự chuyển sang dạng POSIX.
- Thêm `SYSTEMROOT` để Python khởi động được.
- Dùng `taskkill /T` khi quá timeout.

Trên POSIX hành vi giữ nguyên. Không đổi schema hay docstring của tool, không truyền thêm biến chứa credential (đã kiểm tra bằng `env`).

## 2. Các thay đổi đã làm

| File (trong `stage-04-script-skill/`) | Thay đổi |
|---|---|
| `workspace/skills/csv-quality/scripts/check_csv.py` | Thêm `--max-hours` bắt buộc. Hàm `max_hours_arg` tái dùng `parse_hours`; giá trị sai hoặc thiếu thì argparse báo lỗi ra stderr và thoát mã 2. Trong vòng đọc CSV có sẵn, mỗi dòng gom `reasons` theo thứ tự cố định `EXCLUSION_REASONS`. Dòng không có lý do nào thì cộng vào `hours_by_owner`; dòng có lý do thì vào `excluded_rows` đúng một lần. Lần xuất hiện đầu tiên của ID vẫn được ghi vào `first_seen` dù dòng đó không hợp lệ, nên lần sau luôn là `duplicate_id`. Tổng giờ cộng bằng `Decimal` để 1.1 + 2.2 không thành 3.3000000000000003 rồi bị coi là vượt ngưỡng 3.3. Quá tải khi `total > max_hours`. Các trường chất lượng cũ và mã thoát 1 cho lỗi đầu vào giữ nguyên |
| `workspace/skills/csv-quality/SKILL.md` | Thêm mục "Ngưỡng giờ (bắt buộc)": chỉ dùng ngưỡng người dùng nêu trong yêu cầu hiện tại; thiếu thì hỏi lại; không tự chọn ngưỡng, không lấy ngưỡng của cuộc trò chuyện hay lượt trước. Lệnh chạy có `--max-hours <ngưỡng người dùng đưa ra>`. Mô tả các trường JSON mới, mã lý do, exit 2. Bỏ quy tắc cũ "không tính tổng giờ khi còn dữ liệu lỗi" (nay script tự loại dòng lỗi). Không viết cố định số 8 |
| `workspace/skills/csv-quality/references/report-template.md` | Thêm: ngưỡng ở đầu báo cáo, bảng "Tổng giờ theo người", "Người vượt ngưỡng", "Dòng bị loại" (line, task_id, mọi lý do). Giữ các mục chất lượng cũ |
| `fixtures/skills/csv-quality/` | Bản đồng bộ byte-identical của 3 file trên (`diff -r` rỗng), để `reset_workspace.py` không làm mất bài |
| `workspace/data/workload.csv` (stage 03 và 04), `workspace/data/workload-edge.csv` (stage 04) | CSV đầu vào đúng nguyên văn đề |
| `tests/test_check_csv.py` | `run()` truyền `--max-hours`; chạy con với `-X utf8`, giống `PYTHONIOENCODING` mà bash tool đặt (trên Windows stdout của tiến trình con mặc định là cp1252). Thêm test: tổng giờ, quá tải, dòng bị loại; bằng ngưỡng không quá tải; tổng thập phân bằng ngưỡng; **ID đầu tiên có hours không hợp lệ** (`test_first_occurrence_with_invalid_hours_still_blocks_later_duplicate`); nhiều lý do theo thứ tự cố định, strip, phân biệt hoa thường; thiếu hoặc sai `--max-hours` |
| `tests/test_agent.py` | Lệnh mẫu của mock model thêm `--max-hours 10`, vì tham số này giờ là bắt buộc |

Không thêm tool, không sửa `agent.py`, không viết cố định kết quả.

**Kết quả test** (`python -m pytest`):

| Stage | Kết quả |
|---|---|
| stage-04 | 68 passed, 4 failed |
| stage-03 | 44 passed, 4 failed |

Cả 4 test fail ở mỗi stage đều do môi trường Windows và đã fail sẵn ở lab gốc:
- 2 test symlink: `WinError 1314`, cần bật Developer Mode.
- `test_cwd_is_workspace`: Git Bash in `pwd` dạng `/d/...`.
- `test_timeout_kills_process_and_keeps_partial_output`: `sleep` của MSYS giữ pipe nên mất output dở dang.

Code đã được agent `code-reviewer` review. Đã sửa: lỗi cộng số thực ở đúng ngưỡng, CRLF làm diff phình to, PATH dự phòng, giữ nguyên hành vi POSIX của bash.

## 3. Stage 03: Python qua Bash (không có skill)

Kịch bản: `evidence/01-stage03-python-bash/`, trace `20261007-222540_9676d5db_turn01_65fca280.jsonl`.

- Dòng 4–5: `head` + `wc -l` để xem file.
- Dòng 8 (`tool_started`): lệnh Python agent tự viết. Nguyên văn trong `evidence/01-stage03-python-bash/agent-command.sh`.
- Dòng 9 (`tool_finished`, exit 0): stdout `(trống): 2 / Lan: 9 / Minh: 3 / bỏ qua giờ sai: [(5, 'T04', 'Minh', 'abc')]`.

**Tổng của Lan đã đúng (9 giờ), không phải 14.** Đoạn lệnh loại công việc trùng là:
```python
if tid in seen:
    continue  # bỏ qua task_id trùng
seen.add(tid)
```
Dòng 6 (T02 lặp lại) bị bỏ qua nên không bị cộng trùng.

Các dòng được cộng:
- Dòng 2 (T01, Lan, 4), dòng 3 (T02, Lan, 5), dòng 4 (T03, Minh, 3).
- **Dòng 7 (T05, owner trống, 2)** cũng được cộng, vào nhóm "(trống)".
- Dòng 5 (`abc`) bị loại vì `float()` lỗi; dòng 6 bị loại vì trùng ID.

Hai chỗ chưa đúng so với quy tắc của đề:
1. **Không loại dòng thiếu owner:** dòng 7 được cộng thành "(trống): 2", trong khi đề yêu cầu loại dòng này.
2. **Giữ "lần hợp lệ đầu tiên" thay vì "lần xuất hiện đầu tiên":** khi hours sai, lệnh `continue` *trước* `seen.add(tid)`, nên ID đó chưa được đánh dấu là đã gặp. Với `workload.csv` không lộ ra (T04 chỉ xuất hiện một lần). Nhưng chạy lại chính lệnh này trên `workload-edge.csv` thì ra `Lan: 5, Minh: 0` (`evidence/01-stage03-python-bash/agent-command-on-workload-edge.txt`), trong khi kết quả đúng là chỉ Minh 0 giờ và không cộng 5 giờ cho Lan.

Ngoài ra câu trả lời của agent nói T02 trùng ở "dòng 3 và 5", trong khi thực tế là dòng 3 và 6.

Kết luận: code tạm viết qua Bash cho kết quả *trông đúng* trên dữ liệu mẫu nhưng sai quy tắc ở trường hợp biên. Đây là lý do stage 04 đưa quy tắc vào một script đã có test.

## 4. Chạy script trực tiếp

Từ thư mục stage 04: `python workspace/skills/csv-quality/scripts/check_csv.py --input <csv> --max-hours <n>`. Toàn bộ stdout, stderr và mã thoát nằm trong `evidence/00-check-csv-direct/` (`README.md`, `*.json`, `*.stdout.json`).

| Trường hợp | Exit | Kết quả | Đạt |
|---|---|---|---|
| CSV đề bài, ngưỡng 8 | 0 | `hours_by_owner = {Lan: 9, Minh: 3}`, quá tải: Lan. Loại dòng 5 `invalid_hours`, dòng 6 `duplicate_id`, dòng 7 `missing_owner` | ✅ |
| CSV đề bài, ngưỡng 9 | 0 | Tổng giờ và dòng bị loại không đổi; `overloaded_owners = []` | ✅ |
| Trường hợp đặc biệt `workload-edge.csv`, ngưỡng 0 | 0 | `hours_by_owner = {Minh: 0}`, không ai quá tải. Dòng 2 `invalid_hours`, dòng 3 `duplicate_id`; Lan không được cộng 5 giờ | ✅ |
| File không tồn tại | 1 | stderr: `ERROR: Không đọc được file …: No such file or directory`, stdout rỗng | ✅ |
| Thiếu `--max-hours` | 2 | stderr: `the following arguments are required: --max-hours` | ✅ |
| `--max-hours -1` | 2 | stderr: `'-1' không phải số hữu hạn không âm.` | ✅ |

CSV đầu vào không bị sửa sau khi chạy (so sánh từng byte trước và sau).

## 5. Agent stage 04: kết quả từng trường hợp (Qwen)

Mỗi trường hợp là một cuộc trò chuyện mới; câu hỏi không nhắc tên skill hay script. "Dòng N" là số dòng trong file trace JSONL.

| Trường hợp | Kịch bản / trace | Bằng chứng trong trace | Kết quả |
|---|---|---|---|
| Ngưỡng 8: "Kiểm tra data/workload.csv, người nào vượt 8 giờ? Ghi báo cáo vào output/workload.md." | `02-stage04-threshold-8/`, `20261007-222612_3ea459c9_turn01_11002fb0.jsonl` | Dòng 4–7: đọc song song `skills/csv-quality/SKILL.md` và `data/workload.csv` (để xem dữ liệu). Dòng 10, 13: **`bash` chạy `check_csv.py --input data/workload.csv --max-hours 8`, exit 0**, stdout là JSON. Dòng 11–12: đọc `references/report-template.md`. Dòng 16–17: `write_file output/workload.md` | ✅ Báo cáo `stage-04-script-skill/workspace/output/workload.md`: ngưỡng 8; Lan 9 (vượt), Minh 3; loại dòng 5 T04 `invalid_hours`, dòng 6 T02 `duplicate_id`, dòng 7 T05 `missing_owner` |
| Ngưỡng 9 | `03-stage04-threshold-9/`, `20261007-222700_8a4c1684_turn01_7276e5ad.jsonl` | Dòng 11, 13: `--max-hours 9`, exit 0. Dòng 16–17: `write_file output/workload-9.md` | ✅ Không ai quá tải; ghi rõ Lan 9 giờ bằng ngưỡng, không quá tải; dòng bị loại không đổi |
| Không cung cấp ngưỡng: "Tính tổng giờ theo người trong data/workload.csv và xác định người quá tải." | `04-stage04-no-threshold/`, `20261007-222746_4d56baee_turn01_830aab50.jsonl` | Dòng 4–5: chỉ đọc SKILL.md. Không có `bash`. Dòng 8: kết thúc | ✅ Hỏi lại ngưỡng, không chạy script, không kết luận |
| File không tồn tại: "Kiểm tra data/khong-ton-tai.csv, người nào vượt 8 giờ? Ghi báo cáo vào output/khong-ton-tai.md." | `05-stage04-missing-file/`, `20261007-222800_c63f0da5_turn01_a7fe288a.jsonl` | Dòng 4–5: đọc SKILL.md. Dòng 8, 11: `bash` chạy script → **exit_code 1**, stderr `ERROR: Không đọc được file data/khong-ton-tai.csv`. Dòng 14–15: `ls -la data/` để gợi ý file có sẵn. Không có `write_file` | ✅ Báo "không tồn tại, script lỗi thực thi (exit 1), không thể ghi báo cáo như thể đã phân tích"; không đưa tổng giờ; không ghi file |

## 6. Câu hỏi cuối bài

**Phần nào do script tính, phần nào do model diễn giải?**

Script tính toàn bộ phần có đáp án duy nhất, có thể kiểm thử:
- Đọc và parse CSV, chuẩn hóa khoảng trắng.
- Kiểm tra số trường, ID, owner, hours.
- Xác định lần xuất hiện đầu tiên của mỗi ID.
- Cộng tổng giờ theo owner, so sánh với ngưỡng (`>`), lập danh sách người quá tải.
- Lập `excluded_rows` với đủ lý do theo thứ tự cố định.
- Thống kê chất lượng và trả mã thoát (0, 1, 2).

Bằng chứng là kết quả của script trùng khớp ở mọi lần chạy (mục 4 và stdout trong trace).

Model đảm nhận phần cần hiểu ngôn ngữ và ngữ cảnh:
- Nhận ra yêu cầu khớp với skill.
- Lấy ngưỡng từ câu hỏi ("vượt 8 giờ" → `--max-hours 8`), hoặc nhận ra là thiếu ngưỡng để hỏi lại.
- Chọn đường dẫn CSV và file output.
- Đọc `exit_code`/`stderr` để phân biệt lỗi thực thi với lỗi dữ liệu.
- Chuyển JSON thành báo cáo theo template: diễn đạt lý do, viết khuyến nghị.

Khi model **tự tính** (stage 03), kết quả trông đúng trên dữ liệu mẫu nhưng sai quy tắc: cộng dòng thiếu owner và giữ "lần hợp lệ đầu tiên" (mục 3). Phần diễn giải cũng có thể sai: model Mistral 3B từng chép nhầm task_id dòng 7 thành "(trống)" (mục 7). Vì vậy phần nào cần đúng tuyệt đối thì giao cho script; model chỉ nên điều phối và trình bày.

**Nếu sửa script nhưng không cập nhật skill và reference, báo cáo có thể sai hoặc thiếu gì?**
- **Lệnh trong skill cũ thiếu `--max-hours`**, nên script thoát mã 2. Skill cũ chỉ nói về exit 0/1, nên model dễ coi đây là lỗi file và báo "không phân tích được", hoặc tự thêm một ngưỡng tùy ý. Vi phạm yêu cầu "ngưỡng do người dùng cung cấp".
- **Không có quy tắc hỏi lại ngưỡng**: khi người dùng không nêu ngưỡng, model có thể tự chọn (ví dụ 8 hoặc 40) hoặc lấy lại ngưỡng của lượt trước.
- **Skill cũ cấm "tính tổng giờ khi còn dữ liệu lỗi"**: model có thể từ chối báo cáo tổng giờ dù script đã tính đúng; hoặc ngược lại tự cộng như ở stage 03 và sai ở các trường hợp biên.
- **Skill cũ không mô tả `hours_by_owner`, `overloaded_owners`, `excluded_rows`**: model có thể bỏ qua chúng hoặc tự suy lại từ `issues`. Nhầm lẫn dễ gặp: coi người có tổng bằng ngưỡng là quá tải; không biết dòng trùng chỉ giữ lần đầu.
- **Template cũ không có mục ngưỡng, tổng giờ, người vượt ngưỡng, dòng bị loại**: báo cáo theo template cũ thiếu đúng những thông tin đề yêu cầu, chỉ còn thống kê chất lượng, và mục "Đánh giá" còn kết luận là "chưa dùng được để tính tổng giờ".

## 7. Đối chiếu: cùng kịch bản với `ministral-3b-2512` (Mistral)

Thư mục: `evidence/_mistral-ministral-3b/`. Trace gốc và báo cáo của các lần chạy này đã được chuyển vào `_stage-traces/` và `_stage-output/` trong cùng thư mục.

| Trường hợp | Kết quả với model 3B |
|---|---|
| Stage 03 | Dùng pandas; cột `hours` bị đọc thành chuỗi nên ra `Lan,455` / `Minh,3abc`. Lan là chuỗi nối "4"+"5"+"5", **có cả dòng 6 trùng**, tức 14 giờ nếu cộng số. Không có đoạn nào loại dòng trùng |
| Ngưỡng 8, ngưỡng 9 | ✅ Đúng quy trình (skill → script → template → `write_file`). Báo cáo ghi nhầm task_id dòng 7 là "(trống)" thay vì `T05`: lỗi diễn giải dù JSON của script đúng |
| Không nêu ngưỡng | ✅ Hỏi lại ngưỡng |
| File không tồn tại | Lần 1: tự `read_file` file CSV thay vì chạy script (kết luận vẫn đúng). Lần 2: ✅ đi đúng qua script, exit 1 |

So sánh hai model cho thấy: phần do script tính thì hai model cho kết quả giống hệt; khác biệt chỉ nằm ở phần model tự làm (stage 03) và phần diễn giải.

## 8. Hạn chế đã biết

- Vì `--max-hours` là bắt buộc, yêu cầu chỉ kiểm tra chất lượng (không hỏi về quá tải) giờ cũng phải có ngưỡng; theo skill, agent sẽ hỏi lại.
- `workload.csv` và `workload-edge.csv` chỉ nằm trong `workspace/data/` như đề yêu cầu. `reset_workspace.py` sẽ xóa chúng; skill thì đã có bản trong `fixtures/`.
- Mỗi trường hợp với Qwen chạy một lần; chưa đo tỉ lệ đạt qua nhiều lần chạy.
