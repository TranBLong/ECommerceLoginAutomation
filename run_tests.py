#!/usr/bin/env python3
"""Chạy toàn bộ test Login EP + BVA, tạo HTML + Excel report trong một lần chạy."""

import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.test_login_ep_bva import TestLoginEPBVA
from utils.excel_report import export_excel_report, update_source_excel_status


class TimedTestResult(unittest.TextTestResult):
    """Ghi lại thời gian chạy từng test và danh sách test pass."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.successes = []
        self._start_time = None

    def startTest(self, test):
        self._start_time = time.time()
        super().startTest(test)

    def addSuccess(self, test):
        test._duration = round(time.time() - self._start_time, 3)
        self.successes.append(test)
        super().addSuccess(test)

    def addFailure(self, test, err):
        test._duration = round(time.time() - self._start_time, 3)
        super().addFailure(test, err)

    def addError(self, test, err):
        test._duration = round(time.time() - self._start_time, 3)
        super().addError(test, err)


def _export_excel(result):
    try:
        export_excel_report(result)
    except Exception as e:
        print(f"[Cảnh báo] Không xuất được Excel: {e}")
    try:
        source_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testdata", "TestCases_Login_EP_BVA.xlsx")
        update_source_excel_status(result, source_path)
    except Exception as e:
        print(f"[Cảnh báo] Không cập nhật được Status trong Excel nguồn: {e}")


if __name__ == "__main__":
    os.makedirs("reports", exist_ok=True)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestLoginEPBVA)

    runner = None
    try:
        import HtmlTestRunner
        runner = HtmlTestRunner.HTMLTestRunner(
            output="reports",
            report_name="Login_EP_BVA_Report",
            report_title="Login Test Report - EP & BVA",
            combine_reports=True,
            add_timestamp=True,
            verbosity=2,
        )
    except Exception as e:
        print(f"[Cảnh báo] Không dùng được HtmlTestRunner ({e})")
        print("→ Đang dùng TextResult runner thông thường...\n")
        runner = unittest.TextTestRunner(verbosity=2, resultclass=TimedTestResult)

    try:
        result = runner.run(suite)
        _export_excel(result)
        success = getattr(result, "wasSuccessful", lambda: True)()
        sys.exit(0 if success else 1)
    except AttributeError as e:
        print(f"\n[Lỗi HtmlTestRunner] {e}")
        print("→ Chạy lại bằng unittest thuần để xem kết quả chi tiết...\n")
        runner = unittest.TextTestRunner(verbosity=2, resultclass=TimedTestResult)
        result = runner.run(suite)
        _export_excel(result)
        sys.exit(0 if result.wasSuccessful() else 1)
