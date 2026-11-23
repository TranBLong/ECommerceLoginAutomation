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

# Thêm project root vào path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pages.login_page import LoginPage
from utils.browser_setup import BrowserSetup

# Thông báo lỗi thực tế của website
MSG_EMAIL_NOT_FOUND = "The email address was not found."
MSG_WRONG_CREDENTIALS = "email or password not correct"
MSG_EMPTY_EMAIL = "Bạn chưa nhập địa chỉ email"
MSG_EMPTY_PASSWORD = "Bạn chưa nhập mật khẩu"
MSG_MIN_LENGTH = "Yêu cầu tối thiểu 8 ký tự"


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
        cls.valid_email = cls.config["credentials"]["valid_email"]
        cls.valid_password = cls.config["credentials"]["valid_password"]

        # Tài khoản thường có mật khẩu đúng 8 ký tự (biên dưới hợp lệ) - dùng cho BVA
        cls.boundary_email = cls.config.get("boundary_account", "email", fallback="aa@gmail.com")
        cls.boundary_password = cls.config.get("boundary_account", "password", fallback="aA@2aA@2")

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

    # ------------------------------------------------------------------
    # TC_LOGIN_01 - Positive (EP)
    # ------------------------------------------------------------------
    def test_TC_LOGIN_01_valid_login(self):
        """Verify that user can login successfully with valid account"""
        self.page.login(self.valid_email, self.valid_password)

        self.assertTrue(
            self.page.is_login_successful(),
            "Login không thành công với tài khoản hợp lệ (không thấy nút Profile/Admin). URL: "
            + self.page.get_current_url()
        )

    # ------------------------------------------------------------------
    # TC_LOGIN_02 - Negative (EP)
    # ------------------------------------------------------------------
    def test_TC_LOGIN_02_unregistered_email(self):
        """Verify login with unregistered email"""
        self.page.login("notfound_user@gmail.com", self.valid_password)

        self.assertTrue(
            self.page.wait_for_text(MSG_EMAIL_NOT_FOUND),
            f"Không thấy message '{MSG_EMAIL_NOT_FOUND}'. Errors: {self.page.get_all_visible_errors()}"
        )

    # ------------------------------------------------------------------
    # TC_LOGIN_03 - Negative (EP)
    # ------------------------------------------------------------------
    def test_TC_LOGIN_03_incorrect_password(self):
        """Verify login with incorrect password"""
        self.page.login(self.valid_email, "wrongpassword123")

        self.assertTrue(
            self.page.wait_for_text(MSG_WRONG_CREDENTIALS),
            f"Không thấy message '{MSG_WRONG_CREDENTIALS}'. Errors: {self.page.get_all_visible_errors()}"
        )

    # ------------------------------------------------------------------
    # TC_LOGIN_04 - Negative (EP) - thiếu '@' nhưng có đuôi
    # ------------------------------------------------------------------
    def test_TC_LOGIN_04_invalid_email_format(self):
        """Verify login with invalid email format (Missing '@')"""
        self.page.login("adminit24mgmail.com", self.valid_password)

        errors = self.page.get_error_messages()
        # Chỉ chấp nhận đúng lỗi format: "Định dạng phải có '@' trong chuỗi"
        self.assertTrue(
            self._has_error(errors, "Định dạng phải có", "@"),
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
            self._has_error(errors, MSG_EMPTY_EMAIL),
            f"Không thấy lỗi '{MSG_EMPTY_EMAIL}'. Errors: {errors}"
        )

    # ------------------------------------------------------------------
    # TC_LOGIN_06 - Negative (EP)
    # ------------------------------------------------------------------
    def test_TC_LOGIN_06_empty_password(self):
        """Verify login with empty password field"""
        self.page.login(self.valid_email, "")

        errors = self.page.get_error_messages()
        self.assertTrue(
            self._has_error(errors, MSG_EMPTY_PASSWORD),
            f"Không thấy lỗi '{MSG_EMPTY_PASSWORD}'. Errors: {errors}"
        )

    # ------------------------------------------------------------------
    # TC_LOGIN_07 - Negative (EP)
    # ------------------------------------------------------------------
    def test_TC_LOGIN_07_both_empty(self):
        """Verify login with both empty email and password fields"""
        self.page.login("", "")

        errors = self.page.get_error_messages()
        self.assertTrue(self._has_error(errors, MSG_EMPTY_EMAIL), f"Thiếu lỗi email. Errors: {errors}")
        self.assertTrue(self._has_error(errors, MSG_EMPTY_PASSWORD), f"Thiếu lỗi password. Errors: {errors}")

    # ------------------------------------------------------------------
    # TC_LOGIN_08 - Positive (BVA) - biên dưới hợp lệ: 8 ký tự
    # ------------------------------------------------------------------
    def test_TC_LOGIN_08_password_min_boundary(self):
        """Verify login with password length at minimum boundary (8 characters)"""
        self.assertEqual(len(self.boundary_password), 8, "Mật khẩu biên phải đúng 8 ký tự")

        self.page.login(self.boundary_email, self.boundary_password)

        self.assertTrue(
            self.page.is_login_successful(),
            f"Mật khẩu 8 ký tự phải đăng nhập được. Errors: {self.page.get_all_visible_errors()}"
        )

    # ------------------------------------------------------------------
    # TC_LOGIN_09 - Negative (BVA) - dưới biên: 5 ký tự
    # ------------------------------------------------------------------
    def test_TC_LOGIN_09_password_below_min(self):
        """Verify login with password length below minimum boundary (5 characters)"""
        self.page.login(self.valid_email, "12345")

        errors = self.page.get_error_messages()
        self.assertTrue(
            self._has_error(errors, MSG_MIN_LENGTH),
            f"Không thấy lỗi '{MSG_MIN_LENGTH}'. Errors: {errors}"
        )

    # ------------------------------------------------------------------
    # TC_LOGIN_10 - Negative (BVA) - sát dưới biên: 7 ký tự
    # ------------------------------------------------------------------
    def test_TC_LOGIN_10_password_7_chars(self):
        """Verify login with password length just below minimum boundary (7 characters)"""
        self.page.login(self.valid_email, "1234567")

        errors = self.page.get_error_messages()
        self.assertTrue(
            self._has_error(errors, MSG_MIN_LENGTH),
            f"Không thấy lỗi '{MSG_MIN_LENGTH}'. Errors: {errors}"
        )

    # ------------------------------------------------------------------
    # TC_LOGIN_11 - Positive (BVA) - sát trên biên: 9 ký tự
    # Hệ thống KHÔNG báo lỗi độ dài; vì không phải mật khẩu thật nên server báo sai thông tin.
    # ------------------------------------------------------------------
    def test_TC_LOGIN_11_password_9_chars(self):
        """Verify login with password length just above minimum boundary (9 characters)"""
        password_9 = self.boundary_password + "a"
        self.assertEqual(len(password_9), 9)

        self.page.login(self.boundary_email, password_9)

        # Chờ lỗi từ server rồi mới kiểm tra, để chắc chắn form đã được submit
        self.assertTrue(
            self.page.wait_for_text(MSG_WRONG_CREDENTIALS),
            f"Không thấy '{MSG_WRONG_CREDENTIALS}'. Errors: {self.page.get_all_visible_errors()}"
        )
        errors = self.page.get_error_messages()
        self.assertFalse(
            self._has_length_error(errors),
            f"Mật khẩu 9 ký tự không được báo lỗi độ dài. Errors: {errors}"
        )

    # ------------------------------------------------------------------
    # TC_LOGIN_12 - Negative (EP) - thiếu '@' và thiếu đuôi email
    # ------------------------------------------------------------------
    def test_TC_LOGIN_12_email_missing_at_and_domain(self):
        """Verify login with invalid email format (Missing '@' and domain)"""
        self.page.login("admin", self.valid_password)

        errors = self.page.get_error_messages()
        self.assertTrue(
            self._has_error(errors, "Định dạng phải có", "@"),
            f"Không thấy lỗi format email. Errors: {errors}"
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
