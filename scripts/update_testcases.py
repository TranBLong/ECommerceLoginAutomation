#!/usr/bin/env python3
"""
Cập nhật file test case Excel (testdata/TestCases_Login_EP_BVA.xlsx).

Cách dùng (chạy ở thư mục gốc dự án):
    python scripts/update_testcases.py              # sửa nội dung + thêm TC_10, 11, 12
    python scripts/update_testcases.py --sync-status  # như trên + ghi Status từ report Excel mới nhất

Script có thể chạy nhiều lần (idempotent) và luôn sao lưu file gốc vào testdata/backup/.
"""

import argparse
import glob
import os
import shutil
import sys
from copy import copy
from datetime import datetime

from openpyxl import load_workbook

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXCEL_PATH = os.path.join(ROOT, "testdata", "TestCases_Login_EP_BVA.xlsx")
REPORT_GLOB = os.path.join(ROOT, "reports", "Login_EP_BVA_Report_*.xlsx")

URL = "https://e-commerce-for-testing.onrender.com/signin"
PRE = "User is on the Login page"

# Tên cột trong file Excel
COL_TITLE = "Test Summary / Title"
COL_STEPS = "Test Steps"
COL_EXPECTED = "Expected Result"
COL_STATUS = "Status"

# ----- Ô cần sửa: {Test Case ID: {Tên cột: (giá trị cũ cần có hoặc None, giá trị mới)}} -----
EDITS = {
    "TC_LOGIN_01": {
        COL_EXPECTED: "Login successfully. Header shows 'Admin' and 'Profile' buttons "
                      "(the page stays at /signin, no redirect)",
    },
    "TC_LOGIN_08": {
        COL_TITLE: "Verify login with password length at minimum boundary (8 characters)",
        COL_STEPS: f"1. Navigate to url: {URL}\n2. Enter valid email\n"
                   "3. Enter password with exactly 8 chars\n4. Tap on Sign In button",
        COL_EXPECTED: "Login successfully. Header shows 'Profile' button "
                      "(the page stays at /signin, no redirect)",
    },
}

# ----- Dòng mới -----
NEW_ROWS = [
    {
        "Test Case ID": "TC_LOGIN_10",
        COL_TITLE: "Verify login with password length just below minimum boundary (7 characters)",
        "Preconditions": PRE,
        COL_STEPS: f"1. Navigate to url: {URL}\n2. Enter valid email\n"
                   "3. Enter password with 7 chars\n4. Tap on Sign In button",
        "Test Data": "Email: adminit24m@gmail.com\nPassword: 1234567",
        COL_EXPECTED: 'Error message "Yêu cầu tối thiểu 8 ký tự"',
        "Test Type": "Negative (BVA)",
        COL_STATUS: "Untested",
    },
    {
        "Test Case ID": "TC_LOGIN_11",
        COL_TITLE: "Verify login with password length just above minimum boundary (9 characters)",
        "Preconditions": PRE,
        COL_STEPS: f"1. Navigate to url: {URL}\n2. Enter valid email\n"
                   "3. Enter password with 9 chars\n4. Tap on Sign In button",
        "Test Data": "Email: aa@gmail.com\nPassword: aA@2aA@2a",
        COL_EXPECTED: "No length error is shown. Error message 'email or password not correct' "
                      "(password is not the real one)",
        "Test Type": "Positive (BVA)",
        COL_STATUS: "Untested",
    },
    {
        "Test Case ID": "TC_LOGIN_12",
        COL_TITLE: "Verify login with invalid email format (Missing '@' and domain)",
        "Preconditions": PRE,
        COL_STEPS: f"1. Navigate to url: {URL}\n2. Enter email without '@' and domain\n"
                   "3. Enter valid password\n4. Tap on Sign In button",
        "Test Data": "Email: asdasdasdad\nPassword: admin123",
        COL_EXPECTED: "Error message 'Định dạng phải có '@' trong chuỗi'",
        "Test Type": "Negative (EP)",
        COL_STATUS: "Untested",
    },
]


def find_header(ws):
    """Trả về (số dòng header, {tên cột: số cột})."""
    for row in ws.iter_rows(min_row=1, max_row=5):
        names = {str(c.value).strip(): c.column for c in row if c.value}
        if "Test Case ID" in names:
            return row[0].row, names
    sys.exit("Không tìm thấy dòng tiêu đề (cột 'Test Case ID') trong file Excel.")


def find_rows(ws, header_row, id_col):
    rows = {}
    for r in range(header_row + 1, ws.max_row + 1):
        value = ws.cell(r, id_col).value
        if value:
            rows[str(value).strip()] = r
    return rows


def copy_row_style(ws, src_row, dst_row, max_col):
    for c in range(1, max_col + 1):
        src, dst = ws.cell(src_row, c), ws.cell(dst_row, c)
        dst.font = copy(src.font)
        dst.fill = copy(src.fill)
        dst.border = copy(src.border)
        dst.alignment = copy(src.alignment)
        dst.number_format = src.number_format
    ws.row_dimensions[dst_row].height = ws.row_dimensions[src_row].height


def latest_report_results():
    """Đọc report Excel mới nhất do run_tests.py sinh ra → {TC_ID: 'Pass'/'Fail'}."""
    files = sorted(glob.glob(REPORT_GLOB))
    if not files:
        print("[Cảnh báo] Không có file report .xlsx trong thư mục reports/. Bỏ qua --sync-status.")
        return {}
    latest = files[-1]
    print(f"Đọc kết quả từ: {os.path.relpath(latest, ROOT)}")
    ws = load_workbook(latest, data_only=True).active
    results = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        tc_id, status = row[1], row[3]
        if tc_id and str(tc_id).startswith("TC_LOGIN_"):
            results[str(tc_id)] = "Pass" if str(status).upper() == "PASS" else "Fail"
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sync-status", action="store_true", help="ghi Status từ report Excel mới nhất")
    args = parser.parse_args()

    if not os.path.exists(EXCEL_PATH):
        sys.exit(f"Không thấy file: {EXCEL_PATH}")

    # Sao lưu
    backup_dir = os.path.join(ROOT, "testdata", "backup")
    os.makedirs(backup_dir, exist_ok=True)
    backup = os.path.join(backup_dir, f"TestCases_Login_EP_BVA_{datetime.now():%Y-%m-%d_%H-%M-%S}.xlsx")
    shutil.copy2(EXCEL_PATH, backup)
    print(f"Đã sao lưu: {os.path.relpath(backup, ROOT)}")

    wb = load_workbook(EXCEL_PATH)
    ws = wb.active
    header_row, cols = find_header(ws)
    rows = find_rows(ws, header_row, cols["Test Case ID"])
    last_tc_row = max(rows.values())

    # 1. Sửa ô
    for tc_id, changes in EDITS.items():
        r = rows.get(tc_id)
        if not r:
            print(f"[Cảnh báo] Không thấy {tc_id}, bỏ qua.")
            continue
        for col_name, new_value in changes.items():
            cell = ws.cell(r, cols[col_name])
            if cell.value != new_value:
                print(f"Sửa {tc_id} / {col_name}")
                cell.value = new_value

    # 2. Thêm dòng mới (nếu chưa có)
    next_row = last_tc_row + 1
    for new in NEW_ROWS:
        tc_id = new["Test Case ID"]
        if tc_id in rows:
            print(f"{tc_id} đã tồn tại, cập nhật lại nội dung.")
            target = rows[tc_id]
        else:
            target = next_row
            next_row += 1
            copy_row_style(ws, last_tc_row, target, ws.max_column)
            print(f"Thêm {tc_id} vào dòng {target}")
        ws.cell(target, cols["Module"]).value = "LOGIN"
        for col_name, value in new.items():
            ws.cell(target, cols[col_name]).value = value
        rows[tc_id] = target

    # 3. Đồng bộ Status
    if args.sync_status:
        results = latest_report_results()
        for tc_id, status in results.items():
            r = rows.get(tc_id)
            if r:
                ws.cell(r, cols[COL_STATUS]).value = status
                print(f"Status {tc_id} = {status}")

    wb.save(EXCEL_PATH)
    print(f"Đã lưu: {os.path.relpath(EXCEL_PATH, ROOT)}")


if __name__ == "__main__":
    main()
