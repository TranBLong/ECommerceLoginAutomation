"""Xuất báo cáo test ra file Excel."""

import os
import re
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter


def export_excel_report(result, output_dir="reports"):
    """
    Xuất kết quả unittest ra file Excel.
    result: đối tượng TestResult sau khi chạy suite
    (unittest.TextTestResult hoặc HtmlTestRunner.HtmlTestResult).
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(output_dir, f"Login_EP_BVA_Report_{timestamp}.xlsx")

    wb = Workbook()
    ws = wb.active
    ws.title = "Test Report"

    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_fill = PatternFill("solid", fgColor="2F5496")
    pass_fill = PatternFill("solid", fgColor="C6EFCE")
    fail_fill = PatternFill("solid", fgColor="FFC7CE")
    error_fill = PatternFill("solid", fgColor="FFEB9C")
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )
    center = Alignment(horizontal="center", vertical="center", wrap_text=True)

    headers = ["STT", "Test Case ID", "Tên Test Case", "Kết quả", "Thời gian (s)", "Ghi chú / Lỗi"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center
        cell.border = thin_border

    all_tests = _collect_tests(result)
    all_tests.sort(key=lambda x: x["id"] or x["name"])

    for idx, item in enumerate(all_tests, 1):
        row = idx + 1
        values = [
            idx,
            item["id"],
            item["name"],
            item["status"],
            item["time"],
            item["note"],
        ]
        for col, val in enumerate(values, 1):
            cell = ws.cell(row=row, column=col, value=val)
            cell.border = thin_border
            cell.alignment = center if col != 6 else Alignment(wrap_text=True, vertical="center")

            if col == 4:
                if item["status"] == "PASS":
                    cell.fill = pass_fill
                elif item["status"] == "FAIL":
                    cell.fill = fail_fill
                else:
                    cell.fill = error_fill

    summary_row = len(all_tests) + 3
    ws.cell(row=summary_row, column=1, value="TỔNG KẾT").font = Font(bold=True, size=12)

    total = getattr(result, "testsRun", len(all_tests))
    failed = len(getattr(result, "failures", []))
    errors = len(getattr(result, "errors", []))
    passed = total - failed - errors

    ws.cell(row=summary_row + 1, column=1, value="Tổng số test:")
    ws.cell(row=summary_row + 1, column=2, value=total)
    ws.cell(row=summary_row + 2, column=1, value="PASS:")
    ws.cell(row=summary_row + 2, column=2, value=passed).fill = pass_fill
    ws.cell(row=summary_row + 3, column=1, value="FAIL:")
    ws.cell(row=summary_row + 3, column=2, value=failed).fill = fail_fill
    ws.cell(row=summary_row + 4, column=1, value="ERROR:")
    ws.cell(row=summary_row + 4, column=2, value=errors).fill = error_fill

    column_widths = [8, 18, 55, 12, 14, 60]
    for i, width in enumerate(column_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width

    ws.row_dimensions[1].height = 22

    wb.save(filename)
    print(f"\nĐã xuất báo cáo Excel: {filename}")
    return filename


def _collect_tests(result):
    """Chuẩn hóa kết quả từ unittest thuần và HtmlTestRunner."""
    all_tests = []

    for item in getattr(result, "successes", []):
        test = item[0] if isinstance(item, tuple) else item
        all_tests.append(_to_row(test, "PASS", ""))

    for item in getattr(result, "failures", []):
        test, note = _split_outcome(item)
        all_tests.append(_to_row(test, "FAIL", note))

    for item in getattr(result, "errors", []):
        test, note = _split_outcome(item)
        all_tests.append(_to_row(test, "ERROR", note))

    return all_tests


def _split_outcome(item):
    """Tách test và nội dung lỗi từ tuple unittest hoặc _TestInfo của HtmlTestRunner."""
    if isinstance(item, tuple):
        test, traceback = item[0], item[1] if len(item) > 1 else ""
        return test, _short_error(traceback)
    note = getattr(item, "test_exception_info", "") or ""
    return item, _short_error(note)


def _to_row(test, status, note):
    label = _test_label(test)
    duration = getattr(test, "_duration", None)
    if duration in (None, ""):
        duration = getattr(test, "elapsed_time", "")
    if isinstance(duration, float):
        duration = round(duration, 3)
    return {
        "id": _extract_id(label),
        "name": _display_name(test, label),
        "status": status,
        "time": "" if duration in ("", None) else duration,
        "note": note,
    }


def _test_label(test) -> str:
    for attr in ("test_id", "test_description"):
        value = getattr(test, attr, None)
        if value:
            return str(value)
    return str(test)


def _display_name(test, label: str) -> str:
    doc = getattr(test, "_testMethodDoc", None)
    if isinstance(doc, str) and doc.strip():
        return doc.strip().splitlines()[0]
    if "test_TC_LOGIN_" in label:
        start = label.find("test_TC_LOGIN_")
        end = label.find(" ", start)
        if end == -1:
            end = label.find(")", start)
        return label[start:end] if end != -1 else label[start:]
    return label


def _extract_id(name: str) -> str:
    """Lấy TC_LOGIN_xx từ tên test."""
    match = re.search(r"TC_LOGIN_\d+", str(name))
    return match.group(0) if match else ""


def _short_error(traceback_str: str, max_len=300) -> str:
    """Rút gọn traceback, giữ dòng AssertionError."""
    if not traceback_str:
        return ""
    lines = str(traceback_str).strip().splitlines()
    last = lines[-1] if lines else str(traceback_str)
    return last[:max_len]
