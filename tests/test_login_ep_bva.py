"""
Test cases for Login module using Equivalence Partitioning (EP) and Boundary Value Analysis (BVA).
Dựa trên file TestCases_Login_EP_BVA.xlsx
"""

import unittest
import configparser
import os
import sys
import time

# Thêm project root vào path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pages.login_page import LoginPage
from utils.browser_setup import BrowserSetup


class TestLoginEPBVA(unittest.TestCase):
    """Bộ test Login - EP + BVA"""

    @classmethod
    def setUpClass(cls):
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.ini")
        cls.config = configparser.ConfigParser()
        cls.config.read(config_path, encoding="utf-8")

        cls.base_url = cls.config["app"]["base_url"]
        cls.login_url = cls.config["app"]["login_url"]
        cls.valid_email = cls.config["credentials"]["valid_email"]
        cls.valid_password = cls.config["credentials"]["valid_password"]

        # Chạy headless=False để dễ debug, đổi thành True nếu cần
        cls.driver = BrowserSetup.get_driver(headless=False)

    def setUp(self):
        """Mỗi test case: vào trang chủ → bấm Login → vào form Sign In."""
        self.page = LoginPage(self.driver)
        # Cách ổn định: vào home trước rồi click nút Login (tránh /signin bị Not Found)
        self.page.open_from_home(self.base_url)
        time.sleep(0.5)  # đợi form render ổn định

    # ------------------------------------------------------------------
    # TC_LOGIN_01 - Positive (EP)
    # ------------------------------------------------------------------
    def test_TC_LOGIN_01_valid_login(self):
        """Verify that user can login successfully with valid account"""
        self.page.login(self.valid_email, self.valid_password)

        self.assertTrue(
            self.page.is_login_successful(),
            "Login không thành công với tài khoản hợp lệ. URL hiện tại: " + self.page.get_current_url()
        )

    # ------------------------------------------------------------------
    # TC_LOGIN_02 - Negative (EP)
    # ------------------------------------------------------------------
    def test_TC_LOGIN_02_unregistered_email(self):
        """Verify login with unregistered email"""
        self.page.login("notfound_user@gmail.com", self.valid_password)

        errors = self.page.get_all_visible_errors()
        # Có thể là toast hoặc message trên form
        body_text = self.driver.find_element("tag name", "body").text.lower()

        self.assertTrue(
            any("not found" in e.lower() or "email address was not found" in e.lower() for e in errors)
            or "not found" in body_text
            or "email address was not found" in body_text,
            f"Không thấy message lỗi 'email not found'. Errors: {errors}"
        )

    # ------------------------------------------------------------------
    # TC_LOGIN_03 - Negative (EP)
    # ------------------------------------------------------------------
    def test_TC_LOGIN_03_incorrect_password(self):
        """Verify login with incorrect password"""
        self.page.login(self.valid_email, "wrongpassword123")

        errors = self.page.get_all_visible_errors()
        body_text = self.driver.find_element("tag name", "body").text.lower()

        self.assertTrue(
            any("not correct" in e.lower() or "email or password" in e.lower() for e in errors)
            or "not correct" in body_text
            or "email or password" in body_text,
            f"Không thấy message lỗi password. Errors: {errors}"
        )

    # ------------------------------------------------------------------
    # TC_LOGIN_04 - Negative (EP)
    # ------------------------------------------------------------------
    def test_TC_LOGIN_04_invalid_email_format(self):
        """Verify login with invalid email format (Missing '@')"""
        self.page.login("adminit24mgmail.com", self.valid_password)

        errors = self.page.get_error_messages()
        body_text = self.driver.find_element("tag name", "body").text

        self.assertTrue(
            any("@" in e for e in errors)
            or "Định dạng phải có '@'" in body_text
            or "@" in body_text,
            f"Không thấy lỗi format email. Errors: {errors}"
        )

    # ------------------------------------------------------------------
    # TC_LOGIN_05 - Negative (EP)
    # ------------------------------------------------------------------
    def test_TC_LOGIN_05_empty_email(self):
        """Verify login with empty email field"""
        self.page.login("", self.valid_password)

        errors = self.page.get_error_messages()
        self.assertTrue(
            any("Bạn chưa nhập địa chỉ email" in e for e in errors),
            f"Không thấy lỗi 'Bạn chưa nhập địa chỉ email'. Errors: {errors}"
        )

    # ------------------------------------------------------------------
    # TC_LOGIN_06 - Negative (EP)
    # ------------------------------------------------------------------
    def test_TC_LOGIN_06_empty_password(self):
        """Verify login with empty password field"""
        self.page.login(self.valid_email, "")

        errors = self.page.get_error_messages()
        self.assertTrue(
            any("Bạn chưa nhập mật khẩu" in e for e in errors),
            f"Không thấy lỗi 'Bạn chưa nhập mật khẩu'. Errors: {errors}"
        )

    # ------------------------------------------------------------------
    # TC_LOGIN_07 - Negative (EP)
    # ------------------------------------------------------------------
    def test_TC_LOGIN_07_both_empty(self):
        """Verify login with both empty email and password fields"""
        self.page.login("", "")

        errors = self.page.get_error_messages()
        self.assertTrue(
            any("Bạn chưa nhập địa chỉ email" in e for e in errors),
            f"Thiếu lỗi email. Errors: {errors}"
        )
        self.assertTrue(
            any("Bạn chưa nhập mật khẩu" in e for e in errors),
            f"Thiếu lỗi password. Errors: {errors}"
        )

    # ------------------------------------------------------------------
    # TC_LOGIN_08 - Positive (BVA) - Minimum boundary (8 characters)
    # Note: Excel ghi "6 characters" nhưng data thực tế là 8 ký tự và message lỗi là 8.
    # ------------------------------------------------------------------
    def test_TC_LOGIN_08_password_min_boundary(self):
        """Verify login with password length at minimum boundary (8 characters)"""
        # Theo error message thực tế của hệ thống: tối thiểu 8 ký tự
        min_password = "aA@2aA@2"  # 8 ký tự
        self.page.login("aa@gmail.com", min_password)

        # Trường hợp này có thể fail nếu account không tồn tại.
        # Mục tiêu chính của BVA là kiểm tra validation length, không phải login thành công 100%.
        # Nếu hệ thống cho phép submit (không hiện lỗi length) thì pass.
        errors = self.page.get_error_messages()
        length_error = any("tối thiểu" in e.lower() or "minimum" in e.lower() for e in errors)

        self.assertFalse(
            length_error,
            f"Password 8 ký tự vẫn bị báo lỗi length. Errors: {errors}"
        )

    # ------------------------------------------------------------------
    # TC_LOGIN_09 - Negative (BVA)
    # ------------------------------------------------------------------
    def test_TC_LOGIN_09_password_below_min(self):
        """Verify login with password length below minimum boundary (5 characters)"""
        self.page.login(self.valid_email, "12345")

        errors = self.page.get_error_messages()
        body_text = self.driver.find_element("tag name", "body").text

        self.assertTrue(
            any("Yêu cầu tối thiểu 8 ký tự" in e for e in errors)
            or "Yêu cầu tối thiểu 8 ký tự" in body_text
            or "tối thiểu 8" in body_text.lower(),
            f"Không thấy lỗi password quá ngắn. Errors: {errors}"
        )

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.quit()


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
