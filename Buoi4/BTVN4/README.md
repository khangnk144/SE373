# BTVN4: Tool Use & Skill Use (Block 1 + Block 2)

Bài làm trên **bản sao** các stage của `../agent-tools-skills-lab/`; project mẫu giữ nguyên.

- **Block 1:** thêm tool `list_files` + skill `refund-policy`.
- **Block 2:** mở rộng script `check_csv.py` + skill `csv-quality`.

Mọi kịch bản đều đã chạy với model thật, và lưu đủ trace, transcript, request/response API.

**Tóm tắt kết quả:** tất cả yêu cầu của hai block đã làm xong, và mọi trường hợp kiểm tra đều đạt với Qwen3.8-27B (model của UIT). Phân tích chi tiết và vị trí từng bằng chứng trong trace nằm ở [`block1/analysis.md`](block1/analysis.md) và [`block2/analysis.md`](block2/analysis.md).

---

## Block 1: Tra cứu chính sách đúng phiên bản (Stage 00 → 02)

**Mục tiêu của đề:** agent phải tìm được tài liệu chính sách kể cả khi tên file thay đổi, rồi chọn đúng phiên bản theo ngày mua. Đề chỉ cho sửa mã nguồn tool và phần đăng ký tool; không được viết cố định tên file, nội dung chính sách hay đáp án trong system prompt hoặc code tool.

### 1. Chuẩn bị dữ liệu chính sách

- **Đề yêu cầu:** trong bản sao stage 01 và 02, tạo `workspace/data/policies/policy-before-oct.md` và `policy-from-oct.md` với nội dung cho sẵn.
- **Đã làm:** tạo hai file, nội dung chép nguyên văn từ HTML của đề.
- **File:** `block1/stage-01-files/workspace/data/policies/` (tên gốc) và `block1/stage-02-skills/workspace/data/policies/`. Ở stage 02, sau bước "đổi tên", hai file hiện là `tai-lieu-a.md` (chính sách từ tháng 10) và `tai-lieu-b.md` (trước tháng 10).

### 2. Stage 00: xác định giới hạn của agent

- **Đề yêu cầu:** gửi trường hợp A mà không dán chính sách vào chat; ghi lại thông tin và khả năng còn thiếu.
- **Đã làm:** chạy trường hợp A trên stage 00.
- **Bằng chứng:** `block1/evidence/01-stage00-case-a/` và `block1/stage-00-chat/traces/`.
- **Kết quả:** agent không có tool nào nên trả lời từ kiến thức sẵn có: tự nhẩm "8 ngày" rồi đoán "thường 7–14 ngày", không đọc tài liệu nào. Thứ còn thiếu là nội dung và phạm vi hiệu lực của hai chính sách, cùng khả năng tìm và đọc tài liệu. Chi tiết ở `analysis.md`, mục 4.

### 3. Stage 01: cài tool `list_files`

**Đề yêu cầu:**
- Liệt kê mục trực tiếp, không đệ quy; mỗi mục có tên, đường dẫn tương đối và loại `file`/`directory`; sắp theo tên.
- Tái sử dụng cách xử lý đường dẫn và lỗi của tool có sẵn; chặn `..`, path tuyệt đối và symlink ra ngoài.
- Path không tồn tại hoặc path là file phải trả lỗi rõ ràng.
- Đăng ký tool vào schema.

**Đã làm:**
- Thêm hàm `_list()` và tool `list_files()`, dùng lại `_resolve` và `_error` có sẵn.
- Trả lỗi `DIRECTORY_NOT_FOUND`, `NOT_A_DIRECTORY`, `PATH_OUTSIDE_WORKSPACE`.
- Mục con là symlink trỏ ra ngoài workspace thì bị ẩn.
- Đăng ký: `TOOLS = [read_file, write_file, list_files]`.
- Viết thêm 5 unit test.

**File:**
- `block1/stage-01-files/tools/files.py`
- `tools/__init__.py`
- `agent.py`
- `tests/test_files.py`; cập nhật danh sách tool trong `tests/test_agent.py`, `tests/test_app.py`

**Kết quả:**
- Unit test: 39 passed. 3 test fail đều là test tạo symlink, do Windows cần Developer Mode.
- Kiểm tra tool trực tiếp (`block1/check-list-files-tool.py`): đạt 9/9 trường hợp — thư mục hợp lệ, gốc workspace, path là file, path không tồn tại, `..`, `data/../..`, path tuyệt đối, junction trỏ ra ngoài, và junction bị ẩn khi liệt kê. Bằng chứng: `block1/evidence/00-list-files-direct-check/`.
- Thêm một quan sát: ở stage 01, chưa có skill mà agent đã tự dùng `list_files` để tìm và đọc đúng chính sách (`block1/evidence/02-stage01-case-a/`).

### 4. Stage 02: thêm tool + tạo skill `refund-policy`

**Đề yêu cầu:**
- Đưa tool đã viết vào stage 02.
- Tạo `workspace/skills/refund-policy/SKILL.md` và `references/answer-template.md`. Frontmatter có `name` và `description`. Skill hướng dẫn tìm tài liệu trong `data/policies/` và chọn theo ngày mua. Thiếu ngày mua, ngày yêu cầu hoàn hoặc trạng thái kích hoạt thì hỏi lại.
- Reference quy định câu trả lời có: chính sách áp dụng, số ngày đã qua, kết luận, phí, đường dẫn tài liệu.

**Đã làm:**
- Đưa cùng mã nguồn tool, phần đăng ký và test sang stage 02.
- Skill gồm 8 bước:
  1. Chép nguyên văn 3 thông tin; thiếu mục nào thì hỏi lại.
  2. Đọc template.
  3. `list_files data/policies`.
  4. Đọc mọi tài liệu.
  5. Chọn theo ngày mua dựa vào dòng phạm vi hiệu lực.
  6. Đếm số ngày lịch bằng cách liệt kê từng ngày.
  7. Kết luận và lấy phí từ tài liệu.
  8. Trả lời theo template.
- Skill được chỉnh qua 8 phiên bản. Lịch sử và lý do nằm ở `analysis.md`, mục 6.

**File:**
- `block1/stage-02-skills/workspace/skills/refund-policy/SKILL.md`
- `…/refund-policy/references/answer-template.md`
- `block1/stage-02-skills/tools/files.py`, `tools/__init__.py`, `agent.py`, `tests/`

**Kết quả:** unit test 46 passed (3 test symlink fail vì môi trường). Catalog nhận đủ 2 skill, không có cảnh báo.

### 5. Các trường hợp kiểm tra (stage 02, Qwen3.8-27B, mỗi trường hợp một cuộc trò chuyện mới)

| Trường hợp | Đề yêu cầu | Kết quả | Bằng chứng |
|---|---|---|---|
| A: mua 28/09, hoàn 06/10, chưa kích hoạt | Chính sách cũ, 8 ngày, không đủ điều kiện; trace có tìm file, đọc chính sách cũ | ✅ 8 ngày > 7, không đủ điều kiện, căn cứ `data/policies/policy-before-oct.md`; trace có `list_files` và `read_file` | `block1/evidence/03-stage02-case-a/` |
| B: mua 02/10, hoàn 12/10, chưa kích hoạt | Chính sách mới, 10 ngày, đủ điều kiện, không phí; lịch sử có skill + reference | ✅ 10 ngày ≤ 14, đủ điều kiện, không phí, căn cứ `policy-from-oct.md` | `block1/evidence/04-stage02-case-b/` |
| Đổi tên file, chạy lại A | Kết luận không đổi, tìm được file mới | ✅ `list_files` trả `tai-lieu-a.md`, `tai-lieu-b.md`; căn cứ `tai-lieu-b.md`, kết luận giữ nguyên | `block1/evidence/05-stage02-renamed-case-a/` |
| Đổi tên file, chạy lại B | Như trên; không dùng tài liệu từ lịch sử cũ | ✅ Căn cứ `tai-lieu-a.md`; request đầu chỉ có 1 message (cuộc trò chuyện mới); lịch sử có skill + reference | `block1/evidence/06-stage02-renamed-case-b/` |
| Thiếu thông tin | Hỏi trạng thái kích hoạt, không tự giả định | ✅ Chỉ đọc SKILL.md rồi hỏi "đã kích hoạt hay chưa kích hoạt?" | `block1/evidence/07-stage02-missing-info/` |

### 6. Nộp bài Block 1

| Mục nộp | Vị trí |
|---|---|
| Mã nguồn tool mới + đăng ký, stage 01 và 02 | `block1/stage-0{1,2}-*/tools/files.py`, `tools/__init__.py`, `agent.py` |
| Skill `refund-policy/` + hai tài liệu chính sách | `block1/stage-02-skills/workspace/skills/refund-policy/`, `block1/stage-0{1,2}-*/workspace/data/policies/` |
| Trace A, B sau khi đổi tên, thiếu thông tin | `block1/stage-02-skills/traces/` (file `…221913…`, `…222048…`, `…222121…`). Bản sao kèm transcript ở `block1/evidence/03-…`, `06-…`, `07-…` |
| `analysis.md` + câu hỏi cuối bài | `block1/analysis.md`, mục 3 (kiểm tra tool), 5 (từng trường hợp + số dòng trong trace), 7 (câu hỏi cuối) |

---

## Block 2: Kiểm tra quá tải theo người (Stage 03 → 04)

**Mục tiêu của đề:** sửa script kiểm tra CSV để tính tổng giờ theo người, loại dòng không hợp lệ, không cộng trùng công việc; cập nhật skill để dùng ngưỡng người dùng đưa ra. Chỉ được sửa skill `csv-quality` và script có sẵn; không thêm tool, không sửa `agent.py`, không viết cố định kết quả hay ngưỡng 8.

### 1. Chuẩn bị dữ liệu

- **Đề yêu cầu:** tạo `workspace/data/workload.csv` ở bản sao stage 03 và 04.
- **Đã làm:** tạo `workload.csv` ở cả hai stage, và `workload-edge.csv` ở stage 04 cho trường hợp đặc biệt.
- **File:** `block2/stage-03-bash/workspace/data/workload.csv`, `block2/stage-04-script-skill/workspace/data/workload.csv` và `workload-edge.csv`.

### 2. Stage 03: tính tổng giờ bằng Python qua Bash

- **Đề yêu cầu:** xác định những dòng được cộng; nếu Lan ra 14 giờ thì chỉ ra dòng bị cộng trùng, nếu đúng thì chỉ ra đoạn lệnh loại công việc trùng.
- **Kết quả:**
  - Agent tự viết lệnh Python, ra Lan 9 giờ (đúng). Đoạn loại trùng là `if tid in seen: continue`.
  - Nhưng lệnh **vẫn cộng dòng thiếu owner** thành "(trống): 2", và **giữ "lần hợp lệ đầu tiên"** thay vì "lần xuất hiện đầu tiên". Chạy lại chính lệnh đó trên `workload-edge.csv` ra `Lan: 5`, sai quy tắc.
- **Bằng chứng:** `block2/evidence/01-stage03-python-bash/` (gồm `agent-command.sh` và `agent-command-on-workload-edge.txt`). Phân tích ở `block2/analysis.md`, mục 3.

### 3. Stage 04: mở rộng script và cập nhật skill

**Đề yêu cầu:**
- Thêm `--max-hours` bắt buộc; thiếu hoặc sai giá trị thì ghi stderr và thoát mã khác 0.
- Bổ sung `max_hours`, `hours_by_owner`, `overloaded_owners`, `excluded_rows` (mã lý do theo thứ tự cố định); giữ các trường cũ.
- Mỗi ID chỉ giữ lần xuất hiện đầu tiên.
- `SKILL.md`: thiếu ngưỡng thì hỏi lại. Reference: có ngưỡng, tổng giờ, người vượt, dòng bị loại.
- Đồng bộ sang `fixtures/`.

**Đã làm:**
- Mở rộng vòng đọc CSV có sẵn: mỗi dòng gom `reasons`; dòng hợp lệ cộng vào tổng (dùng `Decimal` để tránh lỗi số thực ở đúng ngưỡng); dòng lỗi vào `excluded_rows`.
- Quá tải khi `>` ngưỡng. Mã thoát: 0 khi phân tích được, 1 khi lỗi đầu vào (giữ như cũ), 2 khi `--max-hours` sai hoặc thiếu.
- Cập nhật `SKILL.md` (mục "Ngưỡng giờ (bắt buộc)", các trường JSON mới, exit 2) và template báo cáo.
- Đồng bộ sang `fixtures/`, giống từng byte.

**File:**
- `block2/stage-04-script-skill/workspace/skills/csv-quality/scripts/check_csv.py`
- `…/csv-quality/SKILL.md`
- `…/csv-quality/references/report-template.md`
- `block2/stage-04-script-skill/fixtures/skills/csv-quality/` (bản đồng bộ)

**Test tự động:**
- File: `block2/stage-04-script-skill/tests/test_check_csv.py`.
- Test cho trường hợp đặc biệt: `test_first_occurrence_with_invalid_hours_still_blocks_later_duplicate`.
- Các test khác: tổng giờ, bằng ngưỡng, số thập phân, nhiều lý do, `--max-hours` sai.
- Kết quả: 68 passed. 4 test fail đều do môi trường Windows và đã fail sẵn ở lab gốc.

### 4. Chạy script trực tiếp

| Trường hợp | Kết quả | Bằng chứng |
|---|---|---|
| Ngưỡng 8 | ✅ Lan 9, Minh 3; chỉ Lan quá tải; loại dòng 5 `invalid_hours`, dòng 6 `duplicate_id`, dòng 7 `missing_owner` | `block2/evidence/00-check-csv-direct/threshold-8.stdout.json` |
| Ngưỡng 9 | ✅ Tổng giờ và dòng bị loại không đổi; không ai quá tải | `…/threshold-9.stdout.json` |
| Trường hợp đặc biệt, ngưỡng 0 | ✅ Chỉ Minh 0 giờ; không ai quá tải; dòng 2 `invalid_hours`, dòng 3 `duplicate_id`; không cộng 5 giờ cho Lan | `…/edge-threshold-0.stdout.json` |
| File không tồn tại / thiếu ngưỡng / ngưỡng âm | ✅ exit 1 / 2 / 2, thông báo ra stderr | `…/missing-file.json`, `missing-max-hours.json`, `invalid-max-hours.json` |

### 5. Agent stage 04 (Qwen3.8-27B, mỗi trường hợp một cuộc trò chuyện mới)

| Trường hợp | Đề yêu cầu | Kết quả | Bằng chứng |
|---|---|---|---|
| Ngưỡng 8 | Đọc skill, chạy Bash, nhận JSON, ghi báo cáo | ✅ Skill → `check_csv.py --max-hours 8` → template → `output/workload.md`; Lan 9 vượt ngưỡng | `block2/evidence/02-stage04-threshold-8/`, báo cáo `block2/stage-04-script-skill/workspace/output/workload.md` |
| Ngưỡng 9 | Tổng giờ, dòng bị loại không đổi; không ai quá tải | ✅ `--max-hours 9`; báo cáo `output/workload-9.md` | `block2/evidence/03-stage04-threshold-9/` |
| Không nêu ngưỡng | Hỏi ngưỡng trước khi kết luận | ✅ Chỉ đọc skill rồi hỏi ngưỡng, không chạy script | `block2/evidence/04-stage04-no-threshold/` |
| File không tồn tại | Script lỗi, exit khác 0; agent báo không phân tích được, không có tổng giờ hay báo cáo | ✅ exit 1 + stderr; agent không ghi file nào | `block2/evidence/05-stage04-missing-file/` |

### 6. Nộp bài Block 2

| Mục nộp | Vị trí |
|---|---|
| Skill `csv-quality` (script, hướng dẫn, reference) + bản trong fixtures | `block2/stage-04-script-skill/workspace/skills/csv-quality/`, `…/fixtures/skills/csv-quality/` |
| CSV đầu vào + test tự động | `block2/stage-0{3,4}-*/workspace/data/workload*.csv`, `block2/stage-04-script-skill/tests/test_check_csv.py` |
| JSON chạy trực tiếp với ngưỡng 8, 9, trường hợp đặc biệt | `block2/evidence/00-check-csv-direct/` |
| Báo cáo agent tạo + trace ngưỡng 8, 9, thiếu ngưỡng, file không tồn tại | `block2/stage-04-script-skill/workspace/output/`, `block2/stage-04-script-skill/traces/`, bản sao ở `block2/evidence/02-…` đến `05-…` |
| `analysis.md` + câu hỏi cuối bài | `block2/analysis.md`, mục 2 (thay đổi), 3–5 (kết quả + số dòng trong trace), 6 (câu hỏi cuối) |

---

## Cấu trúc thư mục

```
BTVN4/
├── README.md                    # file này
├── run-scenario.py              # chạy app.py thật (Streamlit AppTest) + lưu bằng chứng đầy đủ
├── uit-tool-call-proxy.py       # proxy thêm tool-call parser cho llm.uit.edu.vn
├── block1/
│   ├── analysis.md
│   ├── check-list-files-tool.py # gọi trực tiếp list_files với các trường hợp của đề
│   ├── stage-00-chat/  stage-01-files/  stage-02-skills/
│   └── evidence/
│       ├── 00-list-files-direct-check/
│       ├── 01-stage00-case-a/ … 07-stage02-missing-info/   # Qwen3.8-27B: bằng chứng nộp
│       └── _mistral-ministral-3b/                          # lần thử với Mistral 3B, skill v1–v8
└── block2/
    ├── analysis.md
    ├── run-check-csv-direct.py  # chạy trực tiếp check_csv.py, lưu stdout/stderr/exit code
    ├── stage-03-bash/  stage-04-script-skill/
    └── evidence/
        ├── 00-check-csv-direct/
        ├── 01-stage03-python-bash/ … 05-stage04-missing-file/   # Qwen3.8-27B: bằng chứng nộp
        └── _mistral-ministral-3b/                               # cùng kịch bản với Mistral 3B (đối chiếu)
```

Mỗi `evidence/<kịch bản>/` gồm:
- `transcript.md`: đọc nhanh prompt, tool call, tool result và câu trả lời.
- `conversation.json`: Conversation JSON của app, gồm messages, snapshots, events.
- `traces/*.jsonl`: bản sao trace do app ghi.
- `api-calls.jsonl`: mọi request/response HTTP, body đầy đủ kèm text gốc của model; không có header hay key.
- `output/`: file agent ghi ra, nếu có.

Không có `.env` hay API key nào trong thư mục này. Đã quét toàn bộ: không file nào chứa key hay header `Authorization`.

## Model và kết nối

**Bằng chứng nộp dùng `qwen3.8-27b` của `llm.uit.edu.vn`, tắt chế độ suy nghĩ.** Có hai trở ngại khi dùng model này:

1. **Máy ở ngoài mạng UIT:** gọi thẳng server thì nhận `HTTP 302 → www.uit.edu.vn`. Cách xử lý: SOCKS tunnel qua SSH tới `192.168.20.150`, giống BTVN3.
2. **Server UIT không bật native tool calling:** gửi `tool_choice="auto"` thì bị HTTP 400. Lab lại yêu cầu endpoint có tool calling và chỉ cho cấu hình model qua `.env`. Cách xử lý: `uit-tool-call-proxy.py` chạy trên máy, gửi `tool_choice="none"` (tools vẫn nằm trong prompt), rồi tách text `<tool_call>…` mà Qwen sinh ra thành `tool_calls` chuẩn OpenAI. Model vẫn tự quyết định gọi tool nào; proxy không thêm hay sửa lời gọi, và text gốc được lưu trong `api-calls.jsonl` (`x_uit_proxy.raw_content`). Không sửa dòng code nào của lab.

**Thử với Mistral `ministral-3b-2512`:**
- Block 1 không ổn định: tính sai số ngày, và lúc thì tự giả định trạng thái kích hoạt, lúc thì hỏi lại dù đã đủ thông tin.
- Block 2 đạt hết.

Bằng chứng giữ trong các thư mục `_mistral-ministral-3b/` để đối chiếu.

## Cách chạy lại

Dùng `.venv` sẵn có của lab: `PY=../agent-tools-skills-lab/.venv/Scripts/python.exe` (Windows). Các bản sao stage nằm ngoài uv workspace của lab, nên gọi thẳng `$PY` thay vì `uv run`.

```bash
# Test (trong thư mục stage)
$PY -m pytest -q -p no:cacheprovider

# Model UIT (khi ở ngoài mạng UIT)
ssh -N -D 127.0.0.1:1080 192.168.20.150                                       # 1. SOCKS tunnel
HTTPS_PROXY=socks5h://127.0.0.1:1080 $PY uit-tool-call-proxy.py --port 8787   # 2. proxy (cần gói socksio)
#   .env: OPENAI_API_KEY=<key UIT>  MODEL_NAME=qwen3.8-27b  OPENAI_BASE_URL=http://127.0.0.1:8787/v1
#   (bản dùng khi làm bài: ../agent-tools-skills-lab/uit-proxy/.env, có .gitignore riêng)

# Chạy một kịch bản và lưu bằng chứng
$PY run-scenario.py --env <file .env> --stage block1/stage-02-skills --out block1/evidence/<tên> "câu hỏi"

# Chạy lại phần kiểm tra trực tiếp
$PY block1/check-list-files-tool.py block1/stage-02-skills block1/evidence/00-list-files-direct-check
$PY block2/run-check-csv-direct.py block2/stage-04-script-skill block2/evidence/00-check-csv-direct

# Mở UI thủ công: chép .env vào thư mục stage rồi chạy
$PY -m streamlit run app.py
```

**Kết quả test:**

| Stage | Kết quả |
|---|---|
| stage-00 | 17 passed |
| stage-01 | 39 passed / 3 failed |
| stage-02 | 46 / 3 |
| stage-03 | 44 / 4 |
| stage-04 | 68 / 4 |

Mọi test fail đều do môi trường Windows và đã fail sẵn ở lab gốc:
- Test tạo symlink cần Developer Mode.
- Git Bash in `pwd` dạng `/d/...`.
- `sleep` của MSYS không trả output dở dang khi timeout.

## Thay đổi môi trường (không thuộc yêu cầu bài)

- **`block2/stage-0{3,4}-*/tools/bash.py`:** trên Windows, `bash` trỏ tới launcher WSL hỏng, nên đã đổi sang Git Bash. Thêm PATH dạng Windows, `SYSTEMROOT`, và `taskkill` khi timeout. Chỉ có tác dụng khi `os.name == "nt"`; trên POSIX hành vi không đổi.
- **`uit-tool-call-proxy.py` + SSH tunnel:** để dùng model UIT (xem mục trên).
- **Gói `socksio`** được cài thêm vào `.venv` của lab để `httpx` đi qua SOCKS. `uv.lock` không đổi.
- **Code review:** agent `code-reviewer` đã review toàn bộ phần code. Đã sửa: lỗi cộng số thực ở đúng ngưỡng, test `test_project` của stage 02, ký tự xuống dòng CRLF, PATH dự phòng của bash.

## Lưu ý trước khi nộp

- Nếu đã chép `.env` vào thư mục stage để mở UI, nhớ xóa trước khi nén hay nộp.
- `reset_workspace.py` xóa mọi thứ trong `workspace/` rồi chép lại từ `fixtures/`. Skill `csv-quality` có bản trong fixtures, nhưng `data/policies/`, skill `refund-policy` và `workload*.csv` thì không, vì đề yêu cầu đặt trong `workspace/`. Đừng chạy reset trên các bản sao này.
