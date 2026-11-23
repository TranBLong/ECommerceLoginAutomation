"""Xuất báo cáo test ra file Excel."""

import os
import re
from datetime import datetime

from openpyxl import Workbook
from openpyxl.chart import PieChart, Reference
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.worksheet.table import Table, TableStyleInfo
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
    summary = wb.create_sheet("Tổng quan")

    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill("solid", fgColor="1F4E78")
    title_fill = PatternFill("solid", fgColor="17365D")
    pass_fill = PatternFill("solid", fgColor="C6EFCE")
    fail_fill = PatternFill("solid", fgColor="FFC7CE")
    error_fill = PatternFill("solid", fgColor="FFE699")
    skipped_fill = PatternFill("solid", fgColor="D9E1F2")
    info_fill = PatternFill("solid", fgColor="D9EAF7")
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )
    center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_wrap = Alignment(horizontal="left", vertical="top", wrap_text=True)

    all_tests = _collect_tests(result)
    all_tests.sort(key=lambda x: x["id"] or x["name"])

    total = getattr(result, "testsRun", len(all_tests))
    pass_count = sum(1 for item in all_tests if item["status"] == "PASS")
    fail_count = sum(1 for item in all_tests if item["status"] == "FAIL")
    error_count = sum(1 for item in all_tests if item["status"] == "ERROR")
    skipped_count = sum(1 for item in all_tests if item["status"] == "SKIP")
    pass_rate = (pass_count / total * 100) if total else 0

    ws.merge_cells("A1:F1")
    ws["A1"] = "LOGIN TEST REPORT - EP & BVA"
    ws["A1"].font = Font(bold=True, color="FFFFFF", size=16)
    ws["A1"].fill = title_fill
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 32

    ws["A2"] = "Thời gian:"
    ws["B2"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    ws["D2"] = "Tỷ lệ PASS:"
    ws["E2"] = f"{pass_rate:.1f}%"
    for cell in ("A2", "D2"):
        ws[cell].font = Font(bold=True)
    for row in ws.iter_rows(min_row=2, max_row=2, min_col=1, max_col=6):
        for cell in row:
            cell.fill = info_fill
            cell.border = thin_border
            cell.alignment = center

    # Summary cards
    cards = [
        ("A4", "TỔNG TEST", "B4", total, "2F5496"),
        ("C4", "PASS", "D4", pass_count, "70AD47"),
        ("A6", "FAIL", "B6", fail_count, "C00000"),
        ("C6", "ERROR", "D6", error_count, "BF9000"),
        ("E4", "SKIP", "F4", skipped_count, "5B9BD5"),
    ]
    for label_cell, label, value_cell, value, color in cards:
        ws[label_cell] = label
        ws[value_cell] = value
        ws[label_cell].font = header_font
        ws[label_cell].fill = PatternFill("solid", fgColor=color)
        ws[label_cell].alignment = center
        ws[label_cell].border = thin_border
        ws[value_cell].font = Font(bold=True, size=14, color=color)
        ws[value_cell].alignment = center
        ws[value_cell].border = thin_border
        ws[value_cell].fill = PatternFill("solid", fgColor="F7F9FC")

    table_header_row = 8
    headers = ["STT", "Test Case ID", "Tên Test Case", "Kết quả", "Thời gian (s)", "Ghi chú / Lỗi"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=table_header_row, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center
        cell.border = thin_border
    ws.row_dimensions[table_header_row].height = 24

    for idx, item in enumerate(all_tests, 1):
        row = idx + table_header_row
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
            cell.alignment = center if col != 6 else left_wrap

            if col == 4:
                if item["status"] == "PASS":
                    cell.fill = pass_fill
                elif item["status"] == "FAIL":
                    cell.fill = fail_fill
                elif item["status"] == "ERROR":
                    cell.fill = error_fill
                elif item["status"] == "SKIP":
                    cell.fill = skipped_fill
        ws.row_dimensions[row].height = 34

    column_widths = [8, 18, 55, 12, 14, 60]
    for i, width in enumerate(column_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width

    ws.freeze_panes = "A9"
    ws.auto_filter.ref = f"A8:F{table_header_row + len(all_tests)}"
    ws.sheet_view.showGridLines = False

    if all_tests:
        table = Table(
            displayName="TestReportTable",
            ref=f"A8:F{table_header_row + len(all_tests)}",
        )
        table.tableStyleInfo = TableStyleInfo(
            name="TableStyleMedium2",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False,
        )
        ws.add_table(table)

    # Overview sheet
    summary.merge_cells("A1:D1")
    summary["A1"] = "TỔNG QUAN KẾT QUẢ TEST"
    summary["A1"].font = Font(bold=True, color="FFFFFF", size=16)
    summary["A1"].fill = title_fill
    summary["A1"].alignment = Alignment(horizontal="center", vertical="center")
    summary.row_dimensions[1].height = 32

    summary_headers = ["Kết quả", "Số lượng", "Tỷ lệ", "Ghi chú"]
    for col, header in enumerate(summary_headers, 1):
        cell = summary.cell(row=3, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center
        cell.border = thin_border

    overview_rows = [
        ("PASS", pass_count, pass_count / total if total else 0, "Test chạy thành công"),
        ("FAIL", fail_count, fail_count / total if total else 0, "Kết quả khác với mong đợi"),
        ("ERROR", error_count, error_count / total if total else 0, "Test/lỗi Selenium bị lỗi"),
        ("SKIP", skipped_count, skipped_count / total if total else 0, "Chưa chạy"),
    ]
    for idx, (status, count, rate, note) in enumerate(overview_rows, 4):
        summary.cell(idx, 1, status)
        summary.cell(idx, 2, count)
        summary.cell(idx, 3, rate)
        summary.cell(idx, 4, note)
        summary.cell(idx, 3).number_format = "0.0%"
        for col in range(1, 5):
            summary.cell(idx, col).border = thin_border
            summary.cell(idx, col).alignment = center if col in (1, 2, 3) else left_wrap
        fill = {"PASS": pass_fill, "FAIL": fail_fill, "ERROR": error_fill, "SKIP": skipped_fill}[status]
        summary.cell(idx, 1).fill = fill

    chart = PieChart()
    chart.title = "Phân bố kết quả"
    chart.add_data(Reference(summary, min_col=2, min_row=3, max_row=7), titles_from_data=True)
    chart.set_categories(Reference(summary, min_col=1, min_row=4, max_row=7))
    chart.height = 7
    chart.width = 10
    chart.legend.position = "r"
    summary.add_chart(chart, "F3")

    for i, width in enumerate([16, 12, 12, 36, 3, 16, 16], 1):
        summary.column_dimensions[get_column_letter(i)].width = width
    summary.freeze_panes = "A3"
    summary.sheet_view.showGridLines = False

    wb.save(filename)
    print(f"\n[OK] Xuat bao cao Excel: {filename}")
    return filename


def update_source_excel_status(result, excel_path="testdata/TestCases_Login_EP_BVA.xlsx"):
    """Cập nhật cột Status trong workbook nguồn theo kết quả test vừa chạy."""
    from openpyxl import load_workbook

    if not os.path.exists(excel_path):
        print(f"[Canh bao] Khong tim thay workbook nguon: {excel_path}")
        return

    status_map = {}
    for item in _collect_tests(result):
        if item["id"]:
            status_map[item["id"]] = {
                "PASS": "Pass",
                "FAIL": "Fail",
                "ERROR": "Error",
            }.get(item["status"], "Untested")

    if not status_map:
        return

    wb = load_workbook(excel_path)
    ws = wb["TestCases_Login"]
    headers = {cell.value: cell.column for cell in ws[1]}
    id_column = headers.get("Test Case ID", 2)
    status_column = headers.get("Status", 9)

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        test_id = row[id_column - 1].value
        if test_id in status_map:
            row[status_column - 1].value = status_map[test_id]

    wb.save(excel_path)
    print(f"[OK] Da cap nhat trang thai test trong workbook: {excel_path}")


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

    for item in getattr(result, "skipped", []):
        if isinstance(item, tuple):
            test, note = item[0], item[1] if len(item) > 1 else ""
            all_tests.append(_to_row(test, "SKIP", str(note)))

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
