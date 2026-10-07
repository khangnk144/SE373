# Kiểm tra trực tiếp list_files: `stage-02-skills`

| # | Trường hợp | path | Mong đợi | Kết quả | Đạt |
|---|---|---|---|---|---|
| 1 | Thư mục hợp lệ | `data/policies` | ok | ok, 2 mục | ✅ |
| 2 | Thư mục gốc workspace | `.` | ok | ok, 4 mục | ✅ |
| 3 | Đường dẫn là file | `data/policies/policy-before-oct.md` | lỗi | lỗi `NOT_A_DIRECTORY` | ✅ |
| 4 | Đường dẫn không tồn tại | `data/khong-ton-tai` | lỗi | lỗi `DIRECTORY_NOT_FOUND` | ✅ |
| 5 | Vượt workspace bằng .. | `..` | lỗi | lỗi `PATH_OUTSIDE_WORKSPACE` | ✅ |
| 6 | Vượt workspace bằng data/../.. | `data/../..` | lỗi | lỗi `PATH_OUTSIDE_WORKSPACE` | ✅ |
| 7 | Đường dẫn tuyệt đối | `D:\UITSTUDY\SE373\Buoi4\BTVN4\block1\stage-02-skills\workspace\data` | lỗi | lỗi `PATH_OUTSIDE_WORKSPACE` | ✅ |
| 8 | Junction trỏ ra ngoài workspace | `data/junction-ra-ngoai` | lỗi | lỗi `PATH_OUTSIDE_WORKSPACE` | ✅ |
| 9 | Liệt kê thư mục chứa junction (junction phải bị ẩn) | `data` | ok | ok, 2 mục | ✅ |

Tool result đầy đủ (JSON string tool trả cho model):

**Thư mục hợp lệ** (`data/policies`)

```json
{"ok": true, "path": "data/policies", "entries": [{"name": "policy-before-oct.md", "path": "data/policies/policy-before-oct.md", "type": "file"}, {"name": "policy-from-oct.md", "path": "data/policies/policy-from-oct.md", "type": "file"}]}
```

**Thư mục gốc workspace** (`.`)

```json
{"ok": true, "path": ".", "entries": [{"name": ".lab-workspace", "path": ".lab-workspace", "type": "file"}, {"name": "data", "path": "data", "type": "directory"}, {"name": "output", "path": "output", "type": "directory"}, {"name": "skills", "path": "skills", "type": "directory"}]}
```

**Đường dẫn là file** (`data/policies/policy-before-oct.md`)

```json
{"ok": false, "error": {"code": "NOT_A_DIRECTORY", "message": "Đây là file, không phải thư mục: data/policies/policy-before-oct.md"}}
```

**Đường dẫn không tồn tại** (`data/khong-ton-tai`)

```json
{"ok": false, "error": {"code": "DIRECTORY_NOT_FOUND", "message": "Không tìm thấy thư mục: data/khong-ton-tai"}}
```

**Vượt workspace bằng ..** (`..`)

```json
{"ok": false, "error": {"code": "PATH_OUTSIDE_WORKSPACE", "message": "Đường dẫn thoát ra ngoài workspace: .."}}
```

**Vượt workspace bằng data/../..** (`data/../..`)

```json
{"ok": false, "error": {"code": "PATH_OUTSIDE_WORKSPACE", "message": "Đường dẫn thoát ra ngoài workspace: data/../.."}}
```

**Đường dẫn tuyệt đối** (`D:\UITSTUDY\SE373\Buoi4\BTVN4\block1\stage-02-skills\workspace\data`)

```json
{"ok": false, "error": {"code": "PATH_OUTSIDE_WORKSPACE", "message": "Không chấp nhận đường dẫn tuyệt đối: D:\\UITSTUDY\\SE373\\Buoi4\\BTVN4\\block1\\stage-02-skills\\workspace\\data. Dùng đường dẫn tương đối workspace."}}
```

**Junction trỏ ra ngoài workspace** (`data/junction-ra-ngoai`)

```json
{"ok": false, "error": {"code": "PATH_OUTSIDE_WORKSPACE", "message": "Đường dẫn thoát ra ngoài workspace: data/junction-ra-ngoai"}}
```

**Liệt kê thư mục chứa junction (junction phải bị ẩn)** (`data`)

```json
{"ok": true, "path": "data", "entries": [{"name": "policies", "path": "data/policies", "type": "directory"}, {"name": "weekly_notes.md", "path": "data/weekly_notes.md", "type": "file"}]}
```
