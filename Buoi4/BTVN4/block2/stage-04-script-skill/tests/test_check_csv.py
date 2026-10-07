"""csv-quality script: thống kê fixture, tổng giờ theo owner, dòng bị loại, ngưỡng --max-hours, lỗi input/schema/parse."""

import json
import subprocess
import sys

import pytest

import paths

SCRIPT = paths.FIXTURES_DIR / "skills" / "csv-quality" / "scripts" / "check_csv.py"
WORKLOAD = "task_id,owner,hours\nT01,Lan,4\nT02,Lan,5\nT03,Minh,3\nT04,Minh,abc\nT02,Lan,5\nT05,,2\n"


def run(path, max_hours="8"):
    # -X utf8: stdout của tiến trình con là UTF-8 cả trên Windows, giống PYTHONIOENCODING mà bash tool đặt
    args = [sys.executable, "-X", "utf8", str(SCRIPT), "--input", str(path)]
    if max_hours is not None:
        args += ["--max-hours", max_hours]
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", timeout=10)


def write_csv(tmp_path, text):
    path = tmp_path / "t.csv"
    path.write_text(text, encoding="utf-8")
    return path


def test_fixture_statistics():
    result = run(paths.FIXTURES_DIR / "data" / "tasks.csv")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["row_count"] == 6
    assert data["missing_owner_count"] == 1
    assert data["invalid_hours_count"] == 1
    assert data["duplicate_id_count"] == 1
    assert data["duplicate_ids"] == ["T02"]
    assert [(i["line"], i["column"], i["type"]) for i in data["issues"]] == [
        (4, "owner", "missing_owner"),
        (5, "hours", "invalid_hours"),
        (6, "task_id", "duplicate_id"),
    ]
    assert "total_hours" not in data


@pytest.mark.parametrize("hours", ["NaN", "nan", "Infinity", "-inf", "-1", ""])
def test_non_finite_negative_or_empty_hours_rejected(tmp_path, hours):
    data = json.loads(run(write_csv(tmp_path, f"task_id,owner,hours\nT01,Lan,{hours}\n")).stdout)
    assert data["invalid_hours_count"] == 1
    assert data["issues"][0]["line"] == 2
    assert data["excluded_rows"] == [{"line": 2, "task_id": "T01", "reasons": ["invalid_hours"]}]
    assert data["hours_by_owner"] == {}


def test_clean_data_exit_0_without_issues(tmp_path):
    result = run(write_csv(tmp_path, "task_id,owner,hours\nT01,Lan,4\nT02,Minh,2.5\n"))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["issues"] == [] and data["excluded_rows"] == []
    assert data["hours_by_owner"] == {"Lan": 4, "Minh": 2.5}


def test_workload_totals_overload_and_excluded_rows(tmp_path):
    result = run(write_csv(tmp_path, WORKLOAD), max_hours="8")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["max_hours"] == 8
    assert data["hours_by_owner"] == {"Lan": 9, "Minh": 3}
    assert data["overloaded_owners"] == [{"owner": "Lan", "total_hours": 9}]
    assert data["excluded_rows"] == [
        {"line": 5, "task_id": "T04", "reasons": ["invalid_hours"]},
        {"line": 6, "task_id": "T02", "reasons": ["duplicate_id"]},
        {"line": 7, "task_id": "T05", "reasons": ["missing_owner"]},
    ]
    assert (data["row_count"], data["duplicate_ids"]) == (6, ["T02"])


def test_total_equal_to_threshold_is_not_overloaded(tmp_path):
    data = json.loads(run(write_csv(tmp_path, WORKLOAD), max_hours="9").stdout)
    assert data["hours_by_owner"] == {"Lan": 9, "Minh": 3}
    assert data["overloaded_owners"] == []
    assert [r["line"] for r in data["excluded_rows"]] == [5, 6, 7]


def test_decimal_total_equal_to_threshold_is_not_overloaded(tmp_path):
    data = json.loads(run(write_csv(tmp_path, "task_id,owner,hours\nA,Lan,1.1\nB,Lan,2.2\n"), max_hours="3.3").stdout)
    assert data["hours_by_owner"] == {"Lan": 3.3}
    assert data["overloaded_owners"] == []


def test_first_occurrence_with_invalid_hours_still_blocks_later_duplicate(tmp_path):
    result = run(write_csv(tmp_path, "task_id,owner,hours\nE01,Lan,abc\nE01,Lan,5\nE02,Minh,0\n"), max_hours="0")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["hours_by_owner"] == {"Minh": 0}
    assert data["overloaded_owners"] == []
    assert data["excluded_rows"] == [
        {"line": 2, "task_id": "E01", "reasons": ["invalid_hours"]},
        {"line": 3, "task_id": "E01", "reasons": ["duplicate_id"]},
    ]


def test_all_reasons_listed_once_in_fixed_order_and_values_stripped(tmp_path):
    text = "task_id,owner,hours\n T01 , Lan , 2 \nT02,lan,1\n,,x\nT03,Minh\nT01,,-1\n\nT04,Hoa,1,thừa\n"
    data = json.loads(run(write_csv(tmp_path, text), max_hours="1").stdout)
    assert data["hours_by_owner"] == {"Lan": 2, "lan": 1}
    assert data["overloaded_owners"] == [{"owner": "Lan", "total_hours": 2}]
    assert data["excluded_rows"] == [
        {"line": 4, "task_id": None, "reasons": ["missing_task_id", "missing_owner", "invalid_hours"]},
        {"line": 5, "task_id": "T03", "reasons": ["wrong_field_count", "invalid_hours"]},
        {"line": 6, "task_id": "T01", "reasons": ["duplicate_id", "missing_owner", "invalid_hours"]},
        {"line": 8, "task_id": "T04", "reasons": ["wrong_field_count"]},
    ]


@pytest.mark.parametrize("max_hours", [None, "", "abc", "-1", "nan", "inf"])
def test_missing_or_invalid_max_hours_exit_non_zero(tmp_path, max_hours):
    result = run(write_csv(tmp_path, WORKLOAD), max_hours=max_hours)
    assert result.returncode != 0
    assert result.stdout == ""
    assert "--max-hours" in result.stderr


def test_missing_file_exit_1(tmp_path):
    result = run(tmp_path / "khong-co.csv")
    assert result.returncode == 1
    assert result.stdout == ""
    assert "Không đọc được file" in result.stderr


def test_missing_column_exit_1(tmp_path):
    result = run(write_csv(tmp_path, "task_id,owner\nT01,Lan\n"))
    assert result.returncode == 1
    assert "Thiếu cột bắt buộc: hours" in result.stderr


def test_parse_error_exit_1(tmp_path):
    result = run(write_csv(tmp_path, 'task_id,owner,hours\nT01,"La"n,4\n'))
    assert result.returncode == 1
    assert "Lỗi parse CSV" in result.stderr


def test_script_does_not_modify_input():
    source = paths.FIXTURES_DIR / "data" / "tasks.csv"
    before = source.read_bytes()
    run(source)
    assert source.read_bytes() == before
