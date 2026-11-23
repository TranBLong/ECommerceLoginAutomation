"""
Test cases for Login module using Equivalence Partitioning (EP) and Boundary Value Analysis (BVA).
Dựa trên file testdata/TestCases_Login_EP_BVA.xlsx (TC_LOGIN_01 → TC_LOGIN_12)

Biến môi trường (tùy chọn):
    OBSERVE=1    giữ màn hình 3 giây sau mỗi test để quan sát / quay video
    HEADLESS=1   chạy trình duyệt ẩn
"""

import unittest
import configparser
import os
import sys
import time
import csv

from dotenv import load_dotenv

# Thêm project root vào path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pages.login_page import LoginPage
from utils.browser_setup import BrowserSetup

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(ROOT, "testdata", "login_data.csv")
load_dotenv(os.path.join(ROOT, ".env"))


def _resolve(value):
    for key in ("VALID_EMAIL", "VALID_PASSWORD", "BOUNDARY_EMAIL", "BOUNDARY_PASSWORD"):
        value = value.replace("{%s}" % key, os.environ.get(key, ""))
    return value


class TestLoginEPBVA(unittest.TestCase):
    """Bộ test Login - EP + BVA"""

    # Chỉ dừng quan sát khi chạy với OBSERVE=1
    OBSERVE_SECONDS = 3 if os.environ.get("OBSERVE") == "1" else 0

    @classmethod
    def setUpClass(cls):
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.ini")
        cls.config = configparser.ConfigParser()
        cls.config.read(config_path, encoding="utf-8")

        cls.base_url = cls.config["app"]["base_url"]
        cls.login_url = cls.config["app"]["login_url"]

        cls.driver = BrowserSetup.get_driver(headless=os.environ.get("HEADLESS") == "1")

    def setUp(self):
        """Mỗi test case: vào trang chủ → bấm Login → vào form Sign In."""
        self.page = LoginPage(self.driver)
        # open_from_home đã tự chờ form Sign In hiển thị, không cần sleep
        self.page.open_from_home(self.base_url)

    def tearDown(self):
        """Giữ màn hình kết quả vài giây (chỉ khi OBSERVE=1)."""
        if self.OBSERVE_SECONDS:
            time.sleep(self.OBSERVE_SECONDS)

    # ------------------------------------------------------------------
    # Hàm hỗ trợ
    # ------------------------------------------------------------------
    def _has_error(self, errors, *keywords):
        """True nếu có ít nhất 1 lỗi chứa đủ tất cả keyword."""
        return any(all(k in e for k in keywords) for e in errors)

    def _has_length_error(self, errors):
        return any("tối thiểu" in e.lower() or "minimum" in e.lower() for e in errors)

    def _screenshot(self):
        os.makedirs(os.path.join(ROOT, "reports", "screenshots"), exist_ok=True)
        name = f"{self._testMethodName}_{time.strftime('%H%M%S')}.png"
        self.driver.save_screenshot(os.path.join(ROOT, "reports", "screenshots", name))

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.quit()


def _make_test(row):
    def test(self):
        email, password = _resolve(row["email"]), _resolve(row["password"])
        texts = [t for t in row["expected_text"].split("|") if t]
        try:
            self.page.login(email, password)
            kind = row["expected_type"]
            if kind == "success":
                self.assertTrue(self.page.is_login_successful(), "Login không thành công")
            elif kind == "server_error":
                for t in texts:
                    self.assertTrue(self.page.wait_for_text(t), f"Không thấy '{t}'")
            elif kind == "form_error":
                errors = self.page.get_error_messages()
                for t in texts:
                    self.assertTrue(self._has_error(errors, t), f"Thiếu '{t}'. Errors: {errors}")
            if row["not_expected_text"]:
                errors = self.page.get_error_messages()
                self.assertFalse(self._has_error(errors, row["not_expected_text"]))
        except Exception:
            self._screenshot()
            raise
    test.__doc__ = row["title"]
    return test


with open(DATA_FILE, encoding="utf-8-sig", newline="") as f:
    for row in csv.DictReader(f):
        setattr(TestLoginEPBVA, f"test_{row['tc_id']}_{row['slug']}", _make_test(row))


if __name__ == "__main__":
    # Chạy với HtmlTestRunner để có report đẹp
    try:
        import HtmlTestRunner
        unittest.main(
            testRunner=HtmlTestRunner.HTMLTestRunner(
                output="reports",
                report_name="Login_EP_BVA_Report",
                report_title="Login Test Report - EP & BVA",
                combine_reports=True,
                add_timestamp=True,
            ),
            verbosity=2,
        )
    except ImportError:
        unittest.main(verbosity=2)
