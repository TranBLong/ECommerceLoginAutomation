from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class LoginPage:
    """Page Object for Sign In page."""

    def __init__(self, driver: WebDriver, timeout: int = 12):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

        # Locators - trang chủ
        self.menu_login_btn = (
            By.XPATH,
            "//button[normalize-space()='Login'] | //a[contains(@href,'/signin')]//button | //a[contains(@href,'/signin')]"
        )

        # Locators - form Sign In
        self.email_input = (By.NAME, "email")
        self.password_input = (By.NAME, "password")
        self.login_button = (By.XPATH, "//button[@type='submit']")
        self.error_messages = (By.CSS_SELECTOR, ".chakra-form__error-message")
        self.any_error = (By.CSS_SELECTOR, ".chakra-form__error-message, [role='alert']")

        # Sau khi login (website KHÔNG chuyển trang, chỉ đổi header)
        self.admin_btn = (By.XPATH, "//button[normalize-space()='Admin'] | //a[contains(.,'Admin')]")
        self.profile_btn = (By.XPATH, "//button[normalize-space()='Profile'] | //a[contains(.,'Profile')]")

    def clear_session(self):
        """Xóa cookie + localStorage + sessionStorage để luôn bắt đầu ở trạng thái chưa login."""
        try:
            self.driver.delete_all_cookies()
        except Exception:
            pass
        try:
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
        except Exception:
            pass

    def open_from_home(self, base_url: str):
        """
        Xóa session → vào trang chủ → bấm nút Login.
        Cách này ổn định, tránh /signin bị Not Found và tránh bị kẹt session đã login.
        """
        self.clear_session()
        self.driver.get(base_url)

        # Nếu vẫn còn đăng nhập (hiện Admin/Profile) thì clear lại và reload
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(self.menu_login_btn)
            )
        except TimeoutException:
            # Có thể đang login → clear mạnh hơn rồi reload
            self.clear_session()
            self.driver.get(base_url)

        login_btn = self.wait.until(EC.element_to_be_clickable(self.menu_login_btn))
        login_btn.click()

        # Đợi form Sign In load xong
        self.wait.until(EC.visibility_of_element_located(self.email_input))

    def open(self, url: str):
        """Mở trực tiếp URL (ít dùng)."""
        self.driver.get(url)

    def enter_email(self, email: str):
        field = self.wait.until(EC.visibility_of_element_located(self.email_input))
        field.clear()
        if email:
            field.send_keys(email)

    def enter_password(self, password: str):
        field = self.wait.until(EC.visibility_of_element_located(self.password_input))
        field.clear()
        if password:
            field.send_keys(password)

    def click_sign_in(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.login_button))
        btn.click()

    def login(self, email: str, password: str):
        self.enter_email(email)
        self.enter_password(password)
        self.click_sign_in()

    def get_error_messages(self) -> list:
        """Trả về danh sách error message inline trên form (không chờ lâu nếu không có lỗi)."""
        try:
            # Chỉ chờ ngắn. Login thành công không có lỗi thì trả về ngay, tránh timeout 12 giây.
            WebDriverWait(self.driver, 1.5).until(
                EC.presence_of_element_located(self.error_messages)
            )
            elements = self.driver.find_elements(*self.error_messages)
            return [el.text.strip() for el in elements if el.text.strip()]
        except TimeoutException:
            return []

    def get_all_visible_errors(self) -> list:
        """Lấy mọi loại error (form + alert/toast)."""
        try:
            elements = self.driver.find_elements(*self.any_error)
            return [el.text.strip() for el in elements if el.text.strip()]
        except Exception:
            return []

    def get_body_text(self) -> str:
        return self.driver.find_element(By.TAG_NAME, "body").text

    def wait_for_text(self, expected: str, timeout: int = 10) -> bool:
        """
        Chờ tới khi body chứa đoạn text (không phân biệt hoa/thường).
        Dùng cho lỗi trả về từ server (khung đỏ), vì lỗi này hiện sau khi có response.
        """
        expected = expected.lower()
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: expected in d.find_element(By.TAG_NAME, "body").text.lower()
            )
            return True
        except TimeoutException:
            return False

    def is_login_successful(self, timeout: int = 10) -> bool:
        """
        Login thành công khi header xuất hiện nút Profile (và Admin nếu là tài khoản admin).
        Lưu ý: website KHÔNG redirect, URL vẫn là /signin nên không dùng URL để kiểm tra.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: len(d.find_elements(*self.profile_btn)) > 0
                or len(d.find_elements(*self.admin_btn)) > 0
            )
            return True
        except TimeoutException:
            return False

    def get_current_url(self) -> str:
        return self.driver.current_url
