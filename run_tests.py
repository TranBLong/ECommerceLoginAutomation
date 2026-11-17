#!/usr/bin/env python3
"""Chạy toàn bộ test Login EP + BVA và tạo HTML report."""

import unittest
import os
import sys

# Đảm bảo import được các module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.test_login_ep_bva import TestLoginEPBVA

if __name__ == "__main__":
    os.makedirs("reports", exist_ok=True)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestLoginEPBVA)

    # Ưu tiên HtmlTestRunner, nếu lỗi version thì fallback TextResult
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
        runner = unittest.TextTestRunner(verbosity=2)

    try:
        result = runner.run(suite)
        success = getattr(result, "wasSuccessful", lambda: True)()
        sys.exit(0 if success else 1)
    except AttributeError as e:
        # Lỗi điển hình: '_count_relevant_tb_levels' của HtmlTestRunner
        print(f"\n[Lỗi HtmlTestRunner] {e}")
        print("→ Chạy lại bằng unittest thuần để xem kết quả chi tiết...\n")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)
