# Block 1: Tra cứu chính sách đúng phiên bản (Stage 00 → 02)

## 1. Môi trường chạy

| Mục | Giá trị |
|---|---|
| Model (bằng chứng nộp) | **Qwen3.8-27B** (`qwen3.8-27b`) của `llm.uit.edu.vn`, tắt chế độ suy nghĩ |
| Kết nối | Máy ngoài mạng UIT → SSH SOCKS tunnel `ssh -N -D 127.0.0.1:1080 192.168.20.150` (giống BTVN3), rồi qua proxy cục bộ `../uit-tool-call-proxy.py` |
| Vì sao cần proxy | Lab yêu cầu endpoint hỗ trợ native tool calling. Server vLLM của UIT không bật `--tool-call-parser`, nên `tool_choice="auto"` bị HTTP 400. Proxy gửi `tool_choice="none"` (tools vẫn được đưa vào prompt) rồi tách text `<tool_call>…` của Qwen thành `tool_calls` chuẩn OpenAI, đúng việc của tool-call parser phía server. **Model tự quyết định gọi tool nào**; proxy không thêm, bớt hay sửa lời gọi. Text gốc của model giữ trong `api-calls.jsonl` (`choices[].x_uit_proxy.raw_content`). Không sửa dòng code nào của lab; chỉ đổi `.env` (`OPENAI_BASE_URL=http://127.0.0.1:8787/v1`, `MODEL_NAME=qwen3.8-27b`) |
| Máy | Windows 11, Python 3.13 trong `.venv` của `agent-tools-skills-lab` (thêm gói `socksio` để `httpx` đi qua SOCKS) |
| Cách chạy agent | `../run-scenario.py` chạy đúng `app.py` của stage qua Streamlit `AppTest` (cách test của lab). Mỗi kịch bản là một lần tải trang + cuộc trò chuyện mới. Trace JSONL do chính app ghi |
| Bằng chứng | `evidence/<kịch bản>/`: `transcript.md`, `conversation.json` (Conversation JSON của app), `traces/*.jsonl`, `api-calls.jsonl` (request/response đầy đủ, không có header/API key) |

Trước đó đã thử `ministral-3b-2512` (Mistral). Kết quả không ổn định, xem mục 6; toàn bộ bằng chứng của lần thử này nằm trong `evidence/_mistral-ministral-3b/`.

## 2. Các thay đổi đã làm

| File | Thay đổi |
|---|---|
| `stage-01-files/tools/files.py` | Thêm `_list(workspace, path)` và tool `list_files(path)`. Dùng lại `_resolve` (chặn path rỗng, path tuyệt đối, `~`, `..`, symlink/junction thoát workspace) và `_error` (cấu trúc `{"ok": false, "error": {code, message}}`). Chỉ liệt kê mục trực tiếp, không đệ quy, sắp theo tên. Mỗi mục có `name`, `path` (tương đối workspace), `type` là `file` hoặc `directory`. Thư mục không tồn tại trả `DIRECTORY_NOT_FOUND`, path là file trả `NOT_A_DIRECTORY`, không trả danh sách rỗng. Mục con là symlink trỏ ra ngoài workspace bị bỏ qua, không lộ thông tin về đích |
| `stage-01-files/tools/__init__.py`, `agent.py` | Đăng ký tool: `TOOLS = [read_file, write_file, list_files]` |
| `stage-01-files/tests/test_files.py` | 5 test mới: liệt kê đúng/không đệ quy/sắp xếp; lỗi khi thư mục không tồn tại hoặc path là file; chặn `..`; chặn path tuyệt đối và path rỗng; chặn symlink thoát workspace. Thêm `list_files.invoke` vào test workspace thật |
| `stage-01-files/tests/test_agent.py`, `test_app.py` | Cập nhật danh sách tool (3 tool) |
| `stage-02-skills/…` | Cùng mã nguồn tool, đăng ký và test như stage 01. `tests/test_project.py`: danh sách `workspace/skills` thêm `refund-policy` |
| `stage-0{1,2}-…/workspace/data/policies/` | Hai tài liệu chính sách, nội dung nguyên văn đề. Ở stage 02, sau bước đổi tên, hai file hiện là `tai-lieu-a.md` (chính sách từ tháng 10) và `tai-lieu-b.md` (trước tháng 10); stage 01 giữ tên gốc |
| `stage-02-skills/workspace/skills/refund-policy/SKILL.md` | Frontmatter `name`, `description` (nhiệm vụ + khi nào dùng). Các bước: (1) chép nguyên văn ngày mua, ngày yêu cầu hoàn, trạng thái kích hoạt; thiếu mục nào thì hỏi lại và dừng, không giả định. (2) Đọc reference. (3) `list_files data/policies`, không đoán và không dùng tên file cũ. (4) Đọc mọi tài liệu. (5) Chọn theo **ngày mua** từ dòng phạm vi hiệu lực (trước X không gồm X; từ X gồm X). (6) Đếm số ngày lịch bằng cách liệt kê từng ngày, có bảng ngày cuối tháng. (7) Kết luận: ≤ giới hạn và chưa kích hoạt thì đủ điều kiện; phí lấy từ tài liệu. (8) Trả lời theo template, dẫn đường dẫn tài liệu |
| `…/refund-policy/references/answer-template.md` | Câu trả lời có: chính sách áp dụng, số ngày đã qua (kèm danh sách đếm), trạng thái kích hoạt, kết luận đủ/không đủ, phí nếu đủ điều kiện, đường dẫn tài liệu căn cứ |

Tuân thủ giới hạn:
- `prompts.py` không đổi.
- Docstring của tool chỉ dùng ví dụ chung (`data`, `output`).
- Không có tên file, nội dung chính sách hay đáp án nào trong system prompt hoặc mã nguồn tool. Tên thư mục `data/policies/` chỉ xuất hiện trong skill, đúng như đề yêu cầu.

Code đã qua agent `code-reviewer`. Đã sửa: test `test_project` của stage 02, CRLF làm diff phình to, wording về định dạng ngày trong skill.

## 3. Kiểm tra tool trực tiếp

Lệnh `python check-list-files-tool.py <stage> evidence/00-list-files-direct-check` gọi `list_files.invoke(...)` đúng như agent gọi. Kết quả nằm trong `evidence/00-list-files-direct-check/stage-0{1,2}-*.md` và `.json`, có đủ JSON tool trả cho model.

| # | Trường hợp | path | Kết quả (cả stage 01 và 02) |
|---|---|---|---|
| 1 | Thư mục hợp lệ | `data/policies` | ✅ `ok`, 2 mục, sắp theo tên, đủ `name`/`path`/`type` |
| 2 | Gốc workspace | `.` | ✅ `ok` |
| 3 | Đường dẫn là file | `data/policies/policy-before-oct.md` | ✅ lỗi `NOT_A_DIRECTORY` |
| 4 | Không tồn tại | `data/khong-ton-tai` | ✅ lỗi `DIRECTORY_NOT_FOUND` |
| 5–6 | Vượt workspace | `..`, `data/../..` | ✅ lỗi `PATH_OUTSIDE_WORKSPACE` |
| 7 | Đường dẫn tuyệt đối | `D:\…\workspace\data` | ✅ lỗi `PATH_OUTSIDE_WORKSPACE` |
| 8 | Junction trỏ ra thư mục tạm chứa file giả | `data/junction-ra-ngoai` | ✅ lỗi `PATH_OUTSIDE_WORKSPACE` |
| 9 | Liệt kê thư mục chứa junction đó | `data` | ✅ junction bị ẩn |

Trường hợp 8–9 dùng *directory junction* thay cho symlink, vì Windows chỉ cho tạo symlink khi bật Developer Mode; junction được tạo tạm rồi xóa ngay.

**Unit test:**

| Stage | Kết quả |
|---|---|
| stage-01 | 39 passed, 3 failed |
| stage-02 | 46 passed, 3 failed |

3 test fail ở mỗi stage là các test tạo symlink (`WinError 1314`), gồm 2 test có sẵn của lab và `test_list_symlink_escape_blocked` mới. Cùng logic này đã được kiểm chứng bằng junction ở trên.

## 4. Stage 00: giới hạn của agent

Kịch bản `evidence/01-stage00-case-a/`, trace `20261007-221410_d46111ba_turn01_4b9496e4.jsonl`:
- Request dòng 2 có 0 tool. Không có lời gọi tool nào; lượt kết thúc ở dòng 4.
- Agent nói không truy cập được hệ thống, rồi trả lời **từ kiến thức sẵn có**: tự nhẩm ra "8 ngày" và đoán "nhiều chương trình… thường có chính sách 7-14 ngày", khuyên liên hệ nơi bán. Nó không đọc tài liệu nào nên không thể kết luận theo chính sách thật.
- **Thông tin còn thiếu:** nội dung và phạm vi hiệu lực của hai phiên bản chính sách (7 ngày + phí 10% so với 14 ngày + không phí).
- **Khả năng còn thiếu:** tìm tài liệu trong workspace (`list_files`), đọc tài liệu (`read_file`), và quy trình chọn phiên bản theo ngày mua (skill).

Thêm: stage 01 chưa có skill, trường hợp A (`evidence/02-stage01-case-a/`, trace `20261007-221426_90f7cd3e_turn01_7a8410d2.jsonl`). Agent tự dùng `list_files` để dò `.` (dòng 4–5), `data` (dòng 8–9), `data/policies` (dòng 12–13), rồi `read_file` cả hai chính sách (dòng 16–19) và kết luận không đủ điều kiện. Như vậy chỉ riêng tool đã đủ để tìm được tài liệu; nhưng agent mất 5 lượt gọi model và không có quy trình hay định dạng câu trả lời thống nhất.

## 5. Kết quả từng trường hợp (stage 02, Qwen)

Mỗi trường hợp là một cuộc trò chuyện mới: request đầu tiên chỉ có 1 message. Câu hỏi không nhắc tên skill, tên file hay thứ tự tool. "Dòng N" là số dòng trong file trace.

| Trường hợp | Kịch bản / trace | Bằng chứng trong trace | Kết quả |
|---|---|---|---|
| **A**: mua 28/09, hoàn 06/10, chưa kích hoạt | `03-stage02-case-a/`, `20261007-221913_987ee0ed_turn01_39a367f9.jsonl` | Dòng 4–5: đọc `SKILL.md`. Dòng 8, 10: đọc `answer-template.md`. Dòng 9, 11: **`list_files data/policies`** → `[policy-before-oct.md, policy-from-oct.md]`. Dòng 14–17: đọc cả hai chính sách. Dòng 18: request cuối có cả skill lẫn reference | ✅ Chính sách trước tháng 10; đếm 29/09…06/10 = **8 ngày** > 7; **không đủ điều kiện**; căn cứ `data/policies/policy-before-oct.md` |
| **B**: mua 02/10, hoàn 12/10, chưa kích hoạt | `04-stage02-case-b/`, `20261007-221952_0d7381ba_turn01_b370526f.jsonl` | Dòng 4–5: skill. Dòng 8–9: reference. Dòng 10–11: `list_files`. Dòng 14–17: đọc chính sách | ✅ Chính sách từ tháng 10; **10 ngày** ≤ 14; **đủ điều kiện, không phí**; căn cứ `data/policies/policy-from-oct.md` |
| **Đổi tên** (`policy-from-oct.md` → `tai-lieu-a.md`, `policy-before-oct.md` → `tai-lieu-b.md`, nội dung giữ nguyên; thứ tự sắp xếp bị đảo), chạy lại A | `05-stage02-renamed-case-a/`, `20261007-222019_7c6105ce_turn01_c3e14254.jsonl` | Dòng 11: `list_files` trả **`[tai-lieu-a.md, tai-lieu-b.md]`**. Dòng 14–17: đọc hai file mới. Request đầu (dòng 2) chỉ có 1 message, không mang lịch sử cũ | ✅ 8 ngày, không đủ điều kiện, căn cứ **`data/policies/tai-lieu-b.md`**: kết luận không đổi |
| **Đổi tên**, chạy lại **B** (trace nộp theo đề) | `06-stage02-renamed-case-b/`, `20261007-222048_3077e548_turn01_1fd53ebf.jsonl` | Dòng 4–5: **skill**. Dòng 8, 10: **reference**. Dòng 9, 11: `list_files` → `[tai-lieu-a.md, tai-lieu-b.md]`. Dòng 14–17: đọc hai file. Dòng 18: request cuối có cả nội dung skill lẫn reference | ✅ 10 ngày, đủ điều kiện, không phí, căn cứ **`data/policies/tai-lieu-a.md`** |
| **Thiếu thông tin**: "Tôi mua ngày 02/10/2026, muốn hoàn ngày 12/10/2026." | `07-stage02-missing-info/`, `20261007-222121_6d78a810_turn01_679f08f7.jsonl` | Dòng 4–5: chỉ đọc `SKILL.md`, không `list_files`, không đọc chính sách. Dòng 8: kết thúc | ✅ Hỏi lại "sản phẩm đã kích hoạt hay chưa kích hoạt?"; không tự giả định, không kết luận |

Trace theo yêu cầu nộp của đề:
- Trường hợp A: `03-stage02-case-a`.
- Trường hợp B sau khi đổi tên file: `06-stage02-renamed-case-b`.
- Thiếu thông tin: `07-stage02-missing-info`.

Bản gốc của các trace nằm trong `stage-0*/traces/`.

## 6. Quá trình làm skill (thử với `ministral-3b-2512`)

Bằng chứng từng phiên bản nằm trong `evidence/_mistral-ministral-3b/_lan-*`.

| Phiên bản | Thay đổi | Kết quả với model 3B |
|---|---|---|
| v1 | Quy trình đầy đủ, công thức trừ ngày | A: tính **9 ngày** (sai). Cả A và B đều **không đọc reference** |
| v2 | Bắt đọc reference ở bước 2 | Đọc reference; A vẫn ra 9 ngày |
| v3 | Bảng số ngày từng tháng; template ghi phép tính | A đúng; B ra **41 ngày**: áp nhầm công thức "khác tháng" |
| v4 | Tách hai nhánh công thức | A đúng; B ra 43 ngày. Chạy thử `ministral-14b` cũng sai |
| v5 | Đếm bằng liệt kê từng ngày | A đúng; B đúng 2/3 lần; đổi tên đúng. Thiếu thông tin: **tự "giả sử chưa kích hoạt"** |
| v6 | Quy tắc dừng tách thành mục riêng | Thiếu thông tin đúng, nhưng A, B **hỏi lại dù đã đủ thông tin** |
| v7 | Nói thêm "không hỏi tên sản phẩm" | Tệ hơn: model quay sang hỏi đúng tên sản phẩm |
| v8 (bản cuối) | Chép nguyên văn 3 thông tin, thiếu mục nào hỏi mục đó | Với 3B đạt 3/5 trường hợp. **Với Qwen 27B: đạt 5/5** (mục 5) |

Bài học:
- Skill càng "cụ thể hóa thao tác" thì càng ổn định: liệt kê ngày thay vì trừ nhẩm; chép nguyên văn thay vì phán đoán "đủ hay thiếu".
- Model nhỏ vẫn không đáng tin ở phần tính toán. Stage 02 chưa có bash/script nên mọi phép tính phải để model làm; đây cũng là lý do Block 2 chuyển phần tính sang script.

## 7. Câu hỏi cuối bài

**Vì sao cần tool để tìm file và skill để hướng dẫn chọn chính sách?**

Hai thứ giải quyết hai vấn đề khác nhau.
- **Tool là năng lực.** Model không nhìn thấy hệ thống file. Chỉ có `read_file` thì model phải biết trước đường dẫn chính xác. `list_files` cho model *quan sát* thư mục tại thời điểm chạy và nhận về tên file thật của lúc đó (trace 05/06, dòng 11: `[tai-lieu-a.md, tai-lieu-b.md]`). Thiếu nó, agent ở stage 00 chỉ có thể đoán ("thường 7-14 ngày").
- **Skill là quy trình nghiệp vụ.** Tool không nói phải dùng tài liệu nào hay áp dụng ra sao. Skill quy định:
  - chọn theo **ngày mua**, không theo ngày yêu cầu hoàn hay tên file;
  - đọc dòng phạm vi hiệu lực ("trước X" không gồm X, "từ X" gồm X);
  - đếm ngày lịch, bằng giới hạn vẫn đủ điều kiện;
  - phí chỉ áp dụng khi đủ điều kiện;
  - thiếu thông tin thì hỏi lại;
  - trả lời theo template và dẫn nguồn.

  Skill chỉ được nạp khi cần: system prompt chỉ có metadata trong catalog. Nhờ vậy context không phình ra với câu hỏi không liên quan. So sánh: stage 01 không có skill vẫn tìm được file nhưng tốn 5 lượt gọi model và trả lời tự do; stage 02 có skill thì 4 lượt, đúng quy trình và đúng template.

**Nếu agent chưa có tool tìm file, sửa prompt có giải quyết được yêu cầu đổi tên file không?**

Không.
- Prompt là văn bản tĩnh viết trước khi chạy, không cho model khả năng quan sát thư mục.
- Ghi tên file vào prompt (vốn bị đề cấm): sau khi đổi tên, `read_file` của tên cũ trả `FILE_NOT_FOUND`, và model không có cách nào biết tên mới, chỉ có thể đoán.
- Dán luôn nội dung chính sách vào prompt: chính sách thành dữ liệu cứng, phải sửa prompt mỗi khi tài liệu đổi hoặc có phiên bản mới, và câu trả lời không còn dẫn được đường dẫn tài liệu thật.
- Prompt có thể dặn "hãy tìm tài liệu", nhưng nếu không có tool nào làm được việc tìm thì lời dặn đó vô dụng.

Đổi tên file là thay đổi trạng thái môi trường lúc chạy, nên phải giải quyết bằng một tool đọc được trạng thái đó.

## 8. Hạn chế đã biết

- Kết quả phụ thuộc model: với `ministral-3b` skill chỉ đạt khoảng 50–70% mỗi trường hợp (mục 6). Bằng chứng nộp dùng Qwen3.8-27B, mỗi trường hợp chạy một lần; chưa đo tỉ lệ đạt qua nhiều lần chạy với Qwen.
- Chạy với model UIT cần tunnel SSH và proxy (`../README.md`). Proxy chỉ hỗ trợ request không stream và định dạng tool call của Qwen.
- `reset_workspace.py` sẽ xóa `data/policies/` và skill `refund-policy`, vì đề yêu cầu đặt chúng trong `workspace/`, không phải `fixtures/`.
